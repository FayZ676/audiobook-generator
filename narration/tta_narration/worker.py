"""Narration as a RunPod serverless worker.

It keeps nothing between jobs. A job brings a chapter's checked script, the
cast, and a clip for each voice the cast uses (a URL or base64, in any
format ffmpeg reads, with its exact transcript):

    {"script": {"segments": [...]}, "cast": {"members": [...]},
     "voices": {"Faizi Standard": {"audio": "https://...", "transcript": "..."}},
     "upload_url": "https://..."}

and gets back the chapter as an MP3 with where each line starts and ends:

    {"duration": 312.4, "lines": [{"id": "seg-0000", "start": 0.0, "end": 2.9}, ...],
     "audio": "<base64 MP3>"}

With upload_url, the MP3 is PUT there (a presigned upload URL from the
caller's storage) and "audio" is left out. RunPod caps what a job can
return, so a whole chapter needs upload_url; base64 suits a line or two.

A job whose input is wrong comes back as {"error": "..."}, which RunPod
reports as a failed job.

    .venv/bin/python -m tta_narration.worker --test_input '{"input": {...}}'
"""

import base64
import logging
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import requests
from pydantic import BaseModel, ValidationError

from tta_narration.narrate import Speaker, VoiceClip, narrate
from tta_narration.speakers import load_speaker
from tta_script.cast import Cast
from tta_script.script import Script

MP3_BITRATE = "64k"  # speech, mono
TIMEOUT_S = 120


class Clip(BaseModel):
    audio: str  # http(s) URL, or base64
    transcript: str


class Job(BaseModel):
    script: Script
    cast: Cast
    voices: dict[str, Clip]
    upload_url: str | None = None


_speaker: Speaker | None = None


def handler(job: dict) -> dict:
    global _speaker  # pylint: disable=global-statement
    try:
        request = Job.model_validate(job["input"])
        with tempfile.TemporaryDirectory() as folder:
            voices = {name: _fetch(clip, Path(folder) / f"{i}") for i, (name, clip) in enumerate(request.voices.items())}
            if _speaker is None:  # loaded once per worker, on its first job
                _speaker = load_speaker()
            narration = narrate(request.script, request.cast, voices, _speaker)
    except (ValidationError, ValueError) as e:
        return {"error": str(e)}

    mp3 = encode_mp3(narration.audio, narration.sample_rate)
    out: dict = {"duration": round(narration.duration, 3), "lines": [vars(line) for line in narration.lines]}
    if request.upload_url:
        requests.put(request.upload_url, data=mp3, headers={"Content-Type": "audio/mpeg"}, timeout=TIMEOUT_S).raise_for_status()
    else:
        out["audio"] = base64.b64encode(mp3).decode()
    return out


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


def encode_mp3(audio: np.ndarray, sample_rate: int) -> bytes:
    return subprocess.run(
        ["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sample_rate), "-ac", "1", "-i", "pipe:0",
         "-b:a", MP3_BITRATE, "-f", "mp3", "pipe:1"],
        input=audio.astype(np.float32).tobytes(), capture_output=True, check=True,
    ).stdout


if __name__ == "__main__":
    import runpod  # type: ignore[import-untyped]

    logging.basicConfig(level=logging.INFO)
    runpod.serverless.start({"handler": handler})
