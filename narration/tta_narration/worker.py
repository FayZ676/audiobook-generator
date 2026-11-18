"""Narration as a RunPod serverless worker that streams.

It keeps nothing between jobs. A job brings a checked script and its cast,
each cast member's voice the name of one of the speech model's own voices
(see tta_narration/models/; e.g. "bm_lewis"):

    {"script": {"segments": [...]}, "cast": {"members": [...]},
     "upload_url": "https://...", "audio_format": "mp3"}

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

With upload_url (an upload URL from the caller's storage), the whole
narration, pauses and all, is PUT there at the end as one MP3 instead, and
each line's chunk carries its timing alone, no audio: start and end are then
where its speech falls in that MP3. The job's results stay small however
long the narration, so they can go to a webhook.

audio_format is "mp3" (the default: 64 kbps) or "m4a" (AAC in an MPEG-4
file, 32 kbps: half the size for one voice, and what .m4a and .m4b files
hold, so a caller joining narrations into one of those needn't re-encode).
It applies to each line's audio and to the upload alike.

A job whose input is wrong yields {"error": "..."} and nothing else.

A {"benchmark": ..., "voice": "bm_lewis"} job measures speed and GPU use instead (see bench.py),
and yields one chunk: each run's numbers, and its audio as base64 MP3.

    .venv/bin/python -m tta_narration.worker --test_input '{"input": {...}}'
"""

import base64
import logging
import time
from collections.abc import Iterator

import io
from typing import Literal

import av
import lameenc  # type: ignore  # a compiled module without type stubs
import numpy as np
import requests
from pydantic import BaseModel, ValidationError

from tta_narration.bench import GpuSampler, benchmark
from tta_narration.narrate import narrate
from tta_narration.speech import SpeechModel, load_speech_model
from tta_script.cast import Cast
from tta_script.script import Script

MP3_KBPS = 64  # speech, mono
AAC_KBPS = 32  # AAC holds one voice as well at half the rate
TIMEOUT_S = 120


class Job(BaseModel):
    script: Script
    cast: Cast
    upload_url: str | None = None
    audio_format: Literal["mp3", "m4a"] = "mp3"


class Benchmark(BaseModel):
    texts: list[str]
    batch_sizes: list[int] = [1, 4, 8, 16]


class BenchmarkJob(BaseModel):
    benchmark: Benchmark
    voice: str


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
    try:
        request = Job.model_validate(job_input)
        if _model is None:  # only when run without __main__, as tests do
            _model = load_speech_model()
        lines = narrate(request.script, request.cast, _model)
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
        chunk: dict = {"id": line.id, "start": line.start, "end": line.end, "pause": line.pause}
        if not request.upload_url:
            chunk["audio"] = _b64(_encode(line.speech, sr, request.audio_format))
        yield chunk
    if request.upload_url:
        requests.put(
            request.upload_url, data=_encode(np.concatenate(whole), sr, request.audio_format),
            headers={"Content-Type": "audio/mp4" if request.audio_format == "m4a" else "audio/mpeg"},
            timeout=TIMEOUT_S,
        ).raise_for_status()
    took = time.monotonic() - started
    log.info("%.1fs of audio in %.1fs (%.2f of real time)", duration, took, took / max(duration, 0.001))
    yield {"done": True, "duration": duration}


def _benchmark(job_input: dict) -> Iterator[dict]:
    global _model  # pylint: disable=global-statement
    try:
        request = BenchmarkJob.model_validate(job_input)
        if _model is None:
            _model = load_speech_model()
        if request.voice not in _model.voices:
            raise ValueError(f"the speech model has no voice {request.voice}")
    except (ValidationError, ValueError) as e:
        yield {"error": str(e)}
        return
    result = benchmark(_model, request.voice, request.benchmark.texts, request.benchmark.batch_sizes)
    for run in result["runs"]:
        log.info("benchmark %s", run)
    sample_rate = _model.sample_rate
    yield {
        "runs": result["runs"],
        "audio": {size: _b64(_mp3(clip, sample_rate)) for size, clip in result["audio"].items()},
    }


def _encode(audio: np.ndarray, sample_rate: int, audio_format: str) -> bytes:
    return _m4a(audio, sample_rate) if audio_format == "m4a" else _mp3(audio, sample_rate)


def _m4a(audio: np.ndarray, sample_rate: int) -> bytes:
    """AAC in an MPEG-4 file, mono. The file's edit list trims the encoder's start-up delay, so the
    speech falls where the line timings say."""
    out = io.BytesIO()
    with av.open(out, "w", format="ipod") as container:
        stream = container.add_stream("aac", rate=sample_rate, layout="mono")
        stream.bit_rate = AAC_KBPS * 1000
        pcm = np.clip(audio, -1, 1).astype(np.float32)
        for i in range(0, len(pcm), sample_rate):  # a second at a time
            frame = av.AudioFrame.from_ndarray(pcm[i:i + sample_rate].reshape(1, -1), format="flt", layout="mono")
            frame.sample_rate = sample_rate
            for packet in stream.encode(frame):
                container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
    return out.getvalue()


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
