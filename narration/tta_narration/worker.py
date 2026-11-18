"""Narration as a RunPod serverless worker that streams.

It keeps nothing between jobs. A job brings a chapter's checked script, the
cast, and a clip for each voice the cast uses (a URL or base64, in any
format ffmpeg reads, with its exact transcript):

    {"script": {"segments": [...]}, "cast": {"members": [...]},
     "voices": {"Faizi Standard": {"audio": "https://...", "transcript": "..."}},
     "upload_url": "https://..."}

It reads the script a line at a time, in order, and sends each line as soon
as it is read: one continuous MP3 stream, cut into chunks.

    {"id": "seg-0000", "start": 0.0, "end": 2.9, "audio": "<base64 MP3 bytes>"}
    ...
    {"done": true, "duration": 312.4, "audio": "<the stream's last bytes>"}

To play while it reads, POST /run and poll GET /stream/<job id>, appending
each chunk's audio bytes, in order, to one MP3 stream. The bytes in a chunk
don't line up exactly with its line (the encoder holds back a few
milliseconds), so seek with start and end, not by chunk. Polling
GET /status/<job id> instead gives every chunk at once when the job is done.

With upload_url (a presigned upload URL from the caller's storage), the
whole MP3 is also PUT there at the end, for keeping.

A job whose input is wrong yields {"error": "..."} and nothing else.

    .venv/bin/python -m tta_narration.worker --test_input '{"input": {...}}'
"""

import base64
import logging
import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path

import lameenc  # type: ignore  # a compiled module without type stubs
import numpy as np
import requests
from pydantic import BaseModel, ValidationError

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


_model: SpeechModel | None = None


def handler(job: dict) -> Iterator[dict]:
    global _model  # pylint: disable=global-statement
    with tempfile.TemporaryDirectory() as folder:
        try:
            request = Job.model_validate(job["input"])
            voices = {name: _fetch(clip, Path(folder) / f"{i}") for i, (name, clip) in enumerate(request.voices.items())}
            if _model is None:  # loaded once per worker, on its first job
                _model = load_speech_model()
            lines = narrate(request.script, request.cast, voices, _model)
        except (ValidationError, ValueError) as e:
            yield {"error": str(e)}
            return

        encoder = Mp3Stream(_model.sample_rate)
        duration = 0.0
        for line in lines:
            duration = line.end
            yield {"id": line.id, "start": line.start, "end": line.end, "audio": _b64(encoder.add(line.audio))}
        tail = encoder.finish()
        if request.upload_url:
            requests.put(
                request.upload_url, data=encoder.whole, headers={"Content-Type": "audio/mpeg"}, timeout=TIMEOUT_S
            ).raise_for_status()
        yield {"done": True, "duration": duration, "audio": _b64(tail)}


class Mp3Stream:
    """Audio in, MP3 bytes out as it comes, as one stream with no gaps
    between the pieces added."""

    def __init__(self, sample_rate: int) -> None:
        self._encoder = lameenc.Encoder()
        self._encoder.set_bit_rate(MP3_KBPS)
        self._encoder.set_in_sample_rate(sample_rate)
        self._encoder.set_channels(1)
        self._encoder.set_quality(2)
        self.whole = b""

    def add(self, audio: np.ndarray) -> bytes:
        pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2").tobytes()
        return self._keep(bytes(self._encoder.encode(pcm)))

    def finish(self) -> bytes:
        return self._keep(bytes(self._encoder.flush()))

    def _keep(self, mp3: bytes) -> bytes:
        self.whole += mp3
        return mp3


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
    # return_aggregate_stream: /status and /runsync give every chunk once done.
    runpod.serverless.start({"handler": handler, "return_aggregate_stream": True})
