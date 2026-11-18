"""How fast a speech model reads, and how hard it works the GPU, at each
batch size: the same sentences read one at a time, then several at once.

Run as a narration job (see worker.py), so it measures the real GPU:

    {"benchmark": {"texts": ["...", ...], "batch_sizes": [1, 4, 8, 16]}, "voice": "bm_lewis"}
"""

import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field

import numpy as np

from tta_narration.speech import SpeechModel


@dataclass
class GpuUse:
    """GPU use sampled every half second while it runs, from nvidia-smi.
    Empty where there's no NVIDIA GPU (a Mac)."""

    utilization: list[int] = field(default_factory=list)  # % of time the GPU was busy
    memory_mb: list[int] = field(default_factory=list)
    total_mb: int = 0

    def summary(self) -> dict:
        if not self.utilization:
            return {}
        return {
            "gpu_busy_mean_pct": round(sum(self.utilization) / len(self.utilization)),
            "gpu_busy_max_pct": max(self.utilization),
            "memory_max_mb": max(self.memory_mb),
            "memory_total_mb": self.total_mb,
        }


class GpuSampler:
    """with GpuSampler() as use: ... fills use with samples taken meanwhile."""

    def __init__(self) -> None:
        self.use = GpuUse()
        self._process: subprocess.Popen | None = None
        self._reader: threading.Thread | None = None

    def __enter__(self) -> GpuUse:
        if shutil.which("nvidia-smi"):
            self._process = subprocess.Popen(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits", "-lms", "500"],
                stdout=subprocess.PIPE, text=True,
            )
            self._reader = threading.Thread(target=self._read, daemon=True)
            self._reader.start()
        return self.use

    def __exit__(self, *_: object) -> None:
        if self._process:
            self._process.terminate()
            self._process.wait()
        if self._reader:
            self._reader.join(timeout=2)

    def _read(self) -> None:
        assert self._process and self._process.stdout
        for row in self._process.stdout:
            try:
                busy, used, total = (int(v) for v in row.split(","))
            except ValueError:  # a MIG slice reports "[N/A]" for what it can't measure
                continue
            self.use.utilization.append(busy)
            self.use.memory_mb.append(used)
            self.use.total_mb = total


def benchmark(model: SpeechModel, voice: str, texts: list[str], batch_sizes: list[int]) -> dict:
    """For each batch size: seconds taken, seconds of audio made, how many
    times faster than real time, and GPU use. The audio is returned too,
    one array per batch size, to check that batching doesn't change what is
    read."""
    model.say(texts[:1], voice)  # the first call sets the GPU up; not counted
    runs, audio = [], {}
    for size in batch_sizes:
        clips: list[np.ndarray] = []
        with GpuSampler() as use:
            started = time.monotonic()
            for i in range(0, len(texts), size):
                clips.extend(model.say(texts[i : i + size], voice))
            took = time.monotonic() - started
        seconds = sum(len(c) for c in clips) / model.sample_rate
        runs.append(
            {
                "batch_size": size,
                "seconds": round(took, 1),
                "audio_seconds": round(seconds, 1),
                "times_real_time": round(seconds / took, 2),
                **use.summary(),
            }
        )
        gap = np.zeros(int(model.sample_rate * 0.4), dtype=np.float32)
        audio[size] = np.concatenate([part for clip in clips for part in (clip, gap)])
    return {"runs": runs, "audio": audio}
