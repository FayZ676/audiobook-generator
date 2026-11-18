"""Kokoro 82M, which reads in its own preset voices.

On a Mac it runs through MLX (about 17x real time on an M1 Pro); on a GPU
(RunPod) through PyTorch. Both read the same way and know the same voices."""

import logging
import multiprocessing
import os
import shutil
import subprocess
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

import numpy as np

from tta_narration.speech import SpeechModel

log = logging.getLogger("tta_narration")
SAMPLE_RATE = 24000
# The English voices. The first letter is the accent (a: American,
# b: British), which picks Kokoro's pronunciation; the second is f or m.
VOICES = frozenset(
    "af_alloy af_aoede af_bella af_heart af_jessica af_kore af_nicole af_nova af_river af_sarah af_sky "
    "am_adam am_echo am_eric am_fenrir am_liam am_michael am_onyx am_puck am_santa "
    "bf_alice bf_emma bf_isabella bf_lily bm_daniel bm_fable bm_george bm_lewis".split()
)
# espeak-ng spells out the words Kokoro's dictionary lacks (names like
# "Netherfield"). The copy pip installs has its build machine's data folder
# compiled in and can't find it, so a system one is used: (library, data).
SYSTEM_ESPEAK = [
    ("/opt/homebrew/lib/libespeak-ng.dylib", "/opt/homebrew/share/espeak-ng-data"),  # brew install espeak-ng
    ("/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1", "/usr/lib/x86_64-linux-gnu/espeak-ng-data"),  # apt
]


def _use_system_espeak() -> None:
    import misaki.espeak  # type: ignore  # noqa: F401  # pylint: disable=import-outside-toplevel,unused-import
    from phonemizer.backend.espeak.wrapper import EspeakWrapper  # type: ignore  # pylint: disable=import-outside-toplevel

    for library, data in SYSTEM_ESPEAK:
        if os.path.exists(library) and os.path.isdir(data):
            EspeakWrapper.set_library(library)
            EspeakWrapper.set_data_path(data)
            return
    raise RuntimeError("Kokoro needs espeak-ng: brew install espeak-ng (Mac) or apt-get install espeak-ng")


def _check(voice: str) -> None:
    if voice not in VOICES:
        raise ValueError(f"Kokoro has no voice {voice!r}")


class KokoroMlx(SpeechModel):
    MODEL = "mlx-community/Kokoro-82M-bf16"
    sample_rate = SAMPLE_RATE
    voices = VOICES

    def __init__(self) -> None:
        from mlx_audio.tts.utils import load_model  # type: ignore  # pylint: disable=import-outside-toplevel

        _use_system_espeak()
        self._model = load_model(model_path=self.MODEL)

    def say(self, texts: list[str], voice: str) -> list[np.ndarray]:
        import mlx.core as mx  # type: ignore  # pylint: disable=import-outside-toplevel

        _check(voice)
        out = []
        for text in texts:
            results = self._model.generate(text, voice=voice, lang_code=voice[0])
            out.append(np.concatenate([np.asarray(r.audio, dtype=np.float32).reshape(-1) for r in results]))
            mx.clear_cache()
        return out


class KokoroTorch(SpeechModel):
    """Kokoro reads one text per pass and is far too small to keep a GPU busy
    alone, so several copies read side by side, each in a process of its own.
    How many is worked out from the machine (see copies_for_this_machine)."""

    sample_rate = SAMPLE_RATE
    voices = VOICES

    def __init__(self) -> None:
        self._copies, why = copies_for_this_machine()
        log.info("Kokoro: %d copies (%s)", self._copies, why)
        self.batch_size = self._copies * 4  # enough texts per call to keep every copy reading
        self._threads = max(1, _cpus() // self._copies)  # each copy's share of the CPU, so they don't fight over it
        self._pool = self._start()

    def _start(self) -> ProcessPoolExecutor:
        # spawn, not fork: CUDA can't be shared with a forked child.
        pool = ProcessPoolExecutor(self._copies, mp_context=multiprocessing.get_context("spawn"),
                                   initializer=_load_copy, initargs=(self._threads,))
        list(pool.map(_ready, range(self._copies)))  # each copy loaded before the first job
        return pool

    def say(self, texts: list[str], voice: str) -> list[np.ndarray]:
        _check(voice)
        try:
            return list(self._pool.map(_read_one, texts, [voice] * len(texts)))
        except BrokenProcessPool as e:
            # A copy died (out of threads or memory, say). The job fails now rather than waiting on
            # it until RunPod's time limit; the copies start afresh for the next job.
            log.error("a Kokoro copy died; starting the copies again")
            self._pool.shutdown(wait=False, cancel_futures=True)
            self._pool = self._start()
            raise RuntimeError("the speech model stopped partway; try again") from e


REPO = "hexgrad/Kokoro-82M"
# GPU memory one copy takes: the model, its working memory and CUDA's own share.
GPU_GB_PER_COPY = 1.5
GPU_HEADROOM_GB = 1.0  # left free, for the odd long text
CPU_CORES_PER_COPY_WITHOUT_GPU = 4  # on a CPU each copy is itself multi-threaded
_pipelines: dict = {}  # in each copy's process: accent -> pipeline, sharing one model


def copies_for_this_machine() -> tuple[int, str]:
    """How many copies to run, and why. Each copy needs GPU memory, and a CPU
    core to prepare its text and keep its GPU work flowing; the scarcer of
    the two decides. TTA_KOKORO_COPIES overrides it."""
    if os.environ.get("TTA_KOKORO_COPIES"):
        return int(os.environ["TTA_KOKORO_COPIES"]), "TTA_KOKORO_COPIES"
    cpus = _cpus()
    free_gb = _free_gpu_gb()
    if free_gb is None:
        by_cpu = max(1, cpus // CPU_CORES_PER_COPY_WITHOUT_GPU)
        return by_cpu, f"no GPU; {cpus} CPU cores"
    by_gpu = max(1, int((free_gb - GPU_HEADROOM_GB) // GPU_GB_PER_COPY))
    copies = min(by_gpu, cpus)
    limit = "GPU memory" if by_gpu <= cpus else "CPU cores"
    return copies, f"{free_gb:.1f} GB GPU memory free fits {by_gpu}, {cpus} CPU cores; {limit} decides"


def _cpus() -> int:
    """The CPUs this process may use. In a container (a RunPod worker) that is
    its quota, e.g. 9 vCPUs on a 48-core host: the host lets it see every
    core but slows it down past its share."""
    seen = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1
    quota = _cgroup_cpus()
    return max(1, min(seen, int(quota))) if quota else seen


def _cgroup_cpus(root: str = "/sys/fs/cgroup") -> float | None:
    """The container's CPU quota in CPUs, or None if it has none: cgroup v2
    (cpu.max: "<quota> <period>") or v1 (cpu.cfs_quota_us, cpu.cfs_period_us)."""
    try:
        with open(f"{root}/cpu.max", encoding="ascii") as f:
            quota, period = f.read().split()
    except (OSError, ValueError):
        try:
            with open(f"{root}/cpu/cpu.cfs_quota_us", encoding="ascii") as q, \
                 open(f"{root}/cpu/cpu.cfs_period_us", encoding="ascii") as p:
                quota, period = q.read().strip(), p.read().strip()
        except OSError:
            return None
    if quota in ("max", "-1"):
        return None
    return int(quota) / int(period)


def _free_gpu_gb() -> float | None:
    """Free memory on the first GPU, from nvidia-smi so this process doesn't
    take a share of the GPU itself. None without an NVIDIA GPU."""
    if not shutil.which("nvidia-smi"):
        return None
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits", "-i", "0"],
        capture_output=True, text=True, check=False,
    )
    try:
        return int(result.stdout.strip()) / 1024
    except ValueError:  # e.g. "[N/A]" on a MIG slice
        return None


def _load_copy(threads: int) -> None:
    # Set before PyTorch loads: its thread pools size themselves on loading, and a copy that started
    # one thread per core of the host (dozens) ran a worker out of threads.
    for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
        os.environ[name] = str(threads)
    # Only on the GPU image, so not importable on a Mac without it.
    import torch  # type: ignore  # pylint: disable=import-outside-toplevel,import-error
    from kokoro import KModel, KPipeline  # type: ignore  # pylint: disable=import-outside-toplevel,import-error

    torch.set_num_threads(threads)
    torch.set_num_interop_threads(1)
    _use_system_espeak()
    model = KModel(repo_id=REPO).to("cuda" if torch.cuda.is_available() else "cpu").eval()
    _pipelines.update({code: KPipeline(lang_code=code, repo_id=REPO, model=model) for code in "ab"})


def _ready(_: int) -> bool:
    return bool(_pipelines)


def _read_one(text: str, voice: str) -> np.ndarray:
    import torch  # type: ignore  # pylint: disable=import-outside-toplevel,import-error

    with torch.inference_mode():
        results = _pipelines[voice[0]](text, voice=voice)
        return np.concatenate([r.audio.cpu().numpy().astype(np.float32).reshape(-1) for r in results])
