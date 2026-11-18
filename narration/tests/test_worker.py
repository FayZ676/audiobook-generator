import base64
import subprocess

import numpy as np
import pytest

from tta_narration import worker
from tta_narration.speech import SpeechModel
from tta_script.cast import NARRATOR_ID, Cast, CastMember
from tta_script.script import Script, ScriptSegment

CAST = Cast(members=[CastMember(id=NARRATOR_ID, names=["Narrator"], age="old", gender="male", voice="deep")])
SCRIPT = Script(segments=[ScriptSegment(id="seg-0", text="Hello there.", speaker_id=NARRATOR_ID)])


class FakeModel(SpeechModel):
    sample_rate = 24000

    def __init__(self):
        self.voices = []

    def say(self, texts, voice):
        with open(voice.path, "rb") as f:
            assert f.read(4) == b"RIFF"  # the clip reaches the model as WAV
        self.voices.append(voice)
        return [np.zeros(24000, dtype=np.float32) for _ in texts]


def clip_mp3() -> str:
    tone = np.sin(np.arange(8000) / 10).astype(np.float32)
    return base64.b64encode(worker.encode_mp3(tone, 8000)).decode()


@pytest.fixture(name="model")
def fake_model(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(worker, "_model", model)
    return model


def job(**extra):
    return {
        "input": {
            "script": SCRIPT.model_dump(),
            "cast": CAST.model_dump(),
            "voices": {"deep": {"audio": clip_mp3(), "transcript": "Hello."}},
            **extra,
        }
    }


def test_returns_an_mp3_and_line_timings(model):
    out = worker.handler(job())

    assert out["lines"] == [{"id": "seg-0", "start": 0.0, "end": 1.0}]
    assert out["duration"] == 1.0
    info = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=format_name", "-of", "csv=p=0", "-"],
        input=base64.b64decode(out["audio"]), capture_output=True, check=True,
    )
    assert info.stdout.strip() == b"mp3"
    assert model.voices[0].transcript == "Hello."


def test_puts_the_mp3_at_the_upload_url(model, monkeypatch):
    puts = []

    class Response:
        def raise_for_status(self):
            pass

    monkeypatch.setattr(worker.requests, "put", lambda url, **kw: puts.append((url, kw)) or Response())

    out = worker.handler(job(upload_url="https://storage.example/ch1.mp3"))

    assert "audio" not in out
    url, kw = puts[0]
    assert url == "https://storage.example/ch1.mp3" and kw["headers"]["Content-Type"] == "audio/mpeg"
    assert model.voices


def test_unreadable_audio_is_an_error(model):
    bad = job()
    bad["input"]["voices"]["deep"]["audio"] = base64.b64encode(b"not audio").decode()

    assert "could not be read" in worker.handler(bad)["error"]
    assert not model.voices


@pytest.mark.usefixtures("model")
def test_a_character_without_a_voice_is_an_error():
    bad = job()
    bad["input"]["voices"] = {}

    assert "no clip for voices deep" in worker.handler(bad)["error"]
