import base64
import subprocess

import numpy as np
import pytest

from tta_narration import worker
from tta_narration.speech import SpeechModel
from tta_script.cast import NARRATOR_ID, Cast, CastMember
from tta_script.script import Script, ScriptSegment

SR = 24000
CAST = Cast(members=[CastMember(id=NARRATOR_ID, names=["Narrator"], age="old", gender="male", voice="deep")])
SCRIPT = Script(
    segments=[
        ScriptSegment(id="seg-0", text="Hello there.", speaker_id=NARRATOR_ID),
        ScriptSegment(id="seg-1", text="Goodbye.", speaker_id=NARRATOR_ID),
    ]
)


class FakeModel(SpeechModel):
    """A second of tone per text."""

    sample_rate = SR

    def __init__(self):
        self.voices = []

    def say(self, texts, voice):
        with open(voice.path, "rb") as f:
            assert f.read(4) == b"RIFF"  # the clip reaches the model as WAV
        self.voices.append(voice)
        tone = 0.3 * np.sin(np.arange(SR) / 5).astype(np.float32)
        return [tone for _ in texts]


@pytest.fixture(name="clip", scope="module")
def clip_m4a(tmp_path_factory) -> str:
    """A short clip in the format phones record."""
    path = tmp_path_factory.mktemp("clip") / "clip.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=duration=1", str(path)], check=True)
    return base64.b64encode(path.read_bytes()).decode()


@pytest.fixture(name="model")
def fake_model(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(worker, "_model", model)
    return model


@pytest.fixture(name="job")
def make_job(clip):
    def job(**extra):
        return {
            "input": {
                "script": SCRIPT.model_dump(),
                "cast": CAST.model_dump(),
                "voices": {"deep": {"audio": clip, "transcript": "Hello."}},
                **extra,
            }
        }

    return job


def duration_of(mp3: bytes) -> float:
    """Seconds of audio the MP3 decodes to, failing on any decoding error."""
    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-xerror", "-f", "mp3", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", str(SR), "pipe:1"],
        input=mp3, capture_output=True, check=True,
    ).stdout
    return len(pcm) / 2 / SR


def test_streams_each_line_then_the_end(model, job):
    chunks = list(worker.handler(job()))

    assert [c.get("id") for c in chunks] == ["seg-0", "seg-1", None]
    assert (chunks[0]["start"], chunks[0]["end"], chunks[0]["pause"]) == (0.0, 1.0, 0.0)
    assert chunks[1]["pause"] > 0 and chunks[1]["start"] == pytest.approx(1.0 + chunks[1]["pause"])
    assert chunks[-1] == {"done": True, "duration": chunks[1]["end"]}
    assert model.voices[0].transcript == "Hello."


def test_each_line_comes_as_its_own_playable_mp3(model, job):
    chunks = list(worker.handler(job()))

    for chunk in chunks[:-1]:
        speech = chunk["end"] - chunk["start"]
        # MP3 adds a few milliseconds of padding to each file.
        assert duration_of(base64.b64decode(chunk["audio"])) == pytest.approx(speech, abs=0.08)
    assert model.voices


def test_puts_the_whole_mp3_at_the_upload_url(model, job, monkeypatch):
    puts = []

    class Response:
        def raise_for_status(self):
            pass

    monkeypatch.setattr(worker.requests, "put", lambda url, **kw: puts.append((url, kw)) or Response())

    chunks = list(worker.handler(job(upload_url="https://storage.example/ch1.mp3")))

    url, kw = puts[0]
    assert url == "https://storage.example/ch1.mp3" and kw["headers"]["Content-Type"] == "audio/mpeg"
    assert duration_of(kw["data"]) == pytest.approx(chunks[-1]["duration"], abs=0.08)
    assert model.voices


def test_unreadable_audio_is_an_error(model, job):
    bad = job()
    bad["input"]["voices"]["deep"]["audio"] = base64.b64encode(b"not audio").decode()

    (chunk,) = worker.handler(bad)

    assert "could not be read" in chunk["error"]
    assert not model.voices


@pytest.mark.usefixtures("model")
def test_a_character_without_a_voice_is_an_error(job):
    bad = job()
    bad["input"]["voices"] = {}

    (chunk,) = worker.handler(bad)

    assert "no clip for voices deep" in chunk["error"]


def test_a_benchmark_reads_the_texts_at_each_batch_size(model, clip):
    calls = []
    say = model.say
    model.say = lambda texts, voice: calls.append(len(texts)) or say(texts, voice)

    (chunk,) = worker.handler(
        {"input": {"benchmark": {"texts": ["One.", "Two.", "Three."], "batch_sizes": [1, 2]}, "voice": {"audio": clip, "transcript": "Hello."}}}
    )

    assert calls == [1, 1, 1, 1, 2, 1]  # a warm-up, then 1+1+1, then 2+1
    assert [(r["batch_size"], r["audio_seconds"]) for r in chunk["runs"]] == [(1, 3.0), (2, 3.0)]
    assert duration_of(base64.b64decode(chunk["audio"][2])) == pytest.approx(3 * 1.4, abs=0.1)
