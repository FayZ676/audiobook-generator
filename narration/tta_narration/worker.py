"""Narration as a RunPod serverless worker that streams.

It keeps nothing between jobs. A job brings a chapter's checked script, the
cast, and a clip for each voice the cast uses (a URL or base64, in any
format ffmpeg reads, with its exact transcript):

    {"script": {"segments": [...]}, "cast": {"members": [...]},
     "voices": {"Faizi Standard": {"audio": "https://...", "transcript": "..."}},
     "upload_url": "https://..."}

It reads the script a line at a time, in order, and sends each line as soon
as it is read, as an MP3 of its own:

    {"id": "seg-0000", "start": 0.0, "end": 2.9, "pause": 0.0, "audio": "<base64 MP3>"}
    {"id": "seg-0001", "start": 3.6, "end": 16.9, "pause": 0.7, "audio": "<base64 MP3>"}
    ...
    {"done": true, "duration": 312.4}

Each line's audio is its speech alone; pause is the silence the narration
puts before it (longer between paragraphs), and start and end are where the
speech falls in the whole narration. A player plays each line after its
pause, and can keep lines to play again without asking for them twice.

To play while it reads, POST /run and poll GET /stream/<job id>. Polling
GET /status/<job id> instead gives every chunk at once when the job is done.

With upload_url (a presigned upload URL from the caller's storage), the
whole narration, pauses and all, is also PUT there at the end as one MP3.

A job whose input is wrong yields {"error": "..."} and nothing else.

A {"benchmark": ...} job measures speed and GPU use instead (see bench.py),
and yields one chunk: each run's numbers, and its audio as base64 MP3.

    .venv/bin/python -m tta_narration.worker --test_input '{"input": {...}}'
"""

import base64
import logging
import time
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path

import lameenc  # type: ignore  # a compiled module without type stubs
import numpy as np
import requests
from pydantic import BaseModel, ValidationError

from tta_narration.bench import GpuSampler, benchmark
from tta_narration.narrate import narrate
from tta_narration.speech import SpeechModel, VoiceClip, load_speech_model
from tta_script.cast import Cast
from tta_script.script import Script

MP3_KBPS = 64  # speech, mono
TIMEOUT_S = 120


class Clip(BaseModel):
    audio: str  # http(s) URL, or base64
    transcript: str


class Job(BaseModel):
    script: Script
    cast: Cast
    voices: dict[str, Clip]
    upload_url: str | None = None


class Benchmark(BaseModel):
    texts: list[str]
    batch_sizes: list[int] = [1, 4, 8, 16]


class BenchmarkJob(BaseModel):
    benchmark: Benchmark
    voice: Clip


log = logging.getLogger("tta_narration")
_model: SpeechModel | None = None  # loaded at boot, before the worker takes jobs


def handler(job: dict) -> Iterator[dict]:
    if "benchmark" in job["input"]:
        yield from _benchmark(job["input"])
        return
    with GpuSampler() as gpu:
        yield from _narrate(job["input"])
    if gpu.utilization:
        log.info("GPU %s", gpu.summary())


def _narrate(job_input: dict) -> Iterator[dict]:
    global _model  # pylint: disable=global-statement
    started = time.monotonic()
    with tempfile.TemporaryDirectory() as folder:
        try:
            request = Job.model_validate(job_input)
            voices = {name: _fetch(clip, Path(folder) / f"{i}") for i, (name, clip) in enumerate(request.voices.items())}
            if _model is None:  # only when run without __main__, as tests do
                _model = load_speech_model()
            lines = narrate(request.script, request.cast, voices, _model)
        except (ValidationError, ValueError) as e:
            yield {"error": str(e)}
            return

        sr = _model.sample_rate
        whole: list[np.ndarray] = []  # the narration, for upload_url
        duration = 0.0
        for line in lines:
            if not duration:
                log.info("first line after %.1fs", time.monotonic() - started)
            duration = line.end
            if request.upload_url:
                whole += [np.zeros(int(sr * line.pause), dtype=np.float32), line.speech]
            yield {
                "id": line.id, "start": line.start, "end": line.end, "pause": line.pause,
                "audio": _b64(_mp3(line.speech, sr)),
            }
        if request.upload_url:
            requests.put(
                request.upload_url, data=_mp3(np.concatenate(whole), sr),
                headers={"Content-Type": "audio/mpeg"}, timeout=TIMEOUT_S,
            ).raise_for_status()
        took = time.monotonic() - started
        log.info("%.1fs of audio in %.1fs (%.2f of real time)", duration, took, took / max(duration, 0.001))
        yield {"done": True, "duration": duration}


def _benchmark(job_input: dict) -> Iterator[dict]:
    global _model  # pylint: disable=global-statement
    with tempfile.TemporaryDirectory() as folder:
        try:
            request = BenchmarkJob.model_validate(job_input)
            voice = _fetch(request.voice, Path(folder) / "voice")
        except (ValidationError, ValueError) as e:
            yield {"error": str(e)}
            return
        if _model is None:
            _model = load_speech_model()
        result = benchmark(_model, voice, request.benchmark.texts, request.benchmark.batch_sizes)
    for run in result["runs"]:
        log.info("benchmark %s", run)
    sample_rate = _model.sample_rate
    yield {
        "runs": result["runs"],
        "audio": {size: _b64(_mp3(clip, sample_rate)) for size, clip in result["audio"].items()},
    }


def _mp3(audio: np.ndarray, sample_rate: int) -> bytes:
    encoder = lameenc.Encoder()
    encoder.set_bit_rate(MP3_KBPS)
    encoder.set_in_sample_rate(sample_rate)
    encoder.set_channels(1)
    encoder.set_quality(2)
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()
    return bytes(encoder.encode(pcm)) + bytes(encoder.flush())


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _fetch(clip: Clip, path: Path) -> VoiceClip:
    """The clip saved as a WAV file the speech model reads."""
    if clip.audio.startswith(("http://", "https://")):
        response = requests.get(clip.audio, timeout=TIMEOUT_S)
        response.raise_for_status()
        data = response.content
    else:
        try:
            data = base64.b64decode(clip.audio.split(",", 1)[-1], validate=True)
        except ValueError as e:
            raise ValueError("a voice's audio is neither a URL nor base64") from e
    path.write_bytes(data)
    wav = path.with_suffix(".wav")
    # Phones record M4A, which the model can't read; ffmpeg reads everything.
    result = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", str(wav)], capture_output=True, check=False)
    if result.returncode:
        raise ValueError(f"a voice's audio could not be read: {result.stderr.decode().strip()}")
    return VoiceClip(str(wav), clip.transcript)


if __name__ == "__main__":
    import runpod  # type: ignore[import-untyped]

    logging.basicConfig(level=logging.INFO)
    # Load before taking jobs, so no listener waits for it: a worker RunPod
    # starts ahead of demand, or restores with FlashBoot, is ready at once.
    loading = time.monotonic()
    _model = load_speech_model()
    log.info("model loaded in %.1fs", time.monotonic() - loading)
    # return_aggregate_stream: /status and /runsync give every chunk once done.
    runpod.serverless.start({"handler": handler, "return_aggregate_stream": True})
