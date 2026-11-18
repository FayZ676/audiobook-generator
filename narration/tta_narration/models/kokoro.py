"""Kokoro 82M, which reads in its own preset voices.

On a Mac it runs through MLX (about 17x real time on an M1 Pro); on a GPU
(RunPod) through PyTorch. Both read the same way and know the same voices."""

import os

import numpy as np

from tta_narration.speech import SpeechModel

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
    REPO = "hexgrad/Kokoro-82M"
    sample_rate = SAMPLE_RATE
    voices = VOICES

    def __init__(self) -> None:
        # Only on the GPU image, so not importable on a Mac without it.
        from kokoro import KModel, KPipeline  # type: ignore  # pylint: disable=import-outside-toplevel,import-error

        _use_system_espeak()
        model = KModel(repo_id=self.REPO).to(_device()).eval()
        # One pipeline per accent, sharing the one model.
        self._pipelines = {code: KPipeline(lang_code=code, repo_id=self.REPO, model=model) for code in "ab"}

    def say(self, texts: list[str], voice: str) -> list[np.ndarray]:
        _check(voice)
        pipeline = self._pipelines[voice[0]]
        return [
            np.concatenate([r.audio.cpu().numpy().astype(np.float32).reshape(-1) for r in pipeline(text, voice=voice)])
            for text in texts
        ]


def _device() -> str:
    import torch  # type: ignore  # pylint: disable=import-outside-toplevel,import-error

    return "cuda" if torch.cuda.is_available() else "cpu"
