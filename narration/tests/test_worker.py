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
    """A second of tone per text; remembers the voices it read in."""

    sample_rate = SR
    voices = frozenset({"deep"})

    def __init__(self):
        self.used = []

    def say(self, texts, voice):
        self.used.append(voice)
        tone = 0.3 * np.sin(np.arange(SR) / 5).astype(np.float32)
        return [tone for _ in texts]


@pytest.fixture(name="model")
def fake_model(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(worker, "_model", model)
    return model


@pytest.fixture(name="job")
def make_job():
    def job(**extra):
        return {
            "input": {
                "script": SCRIPT.model_dump(),
                "cast": CAST.model_dump(),
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
    assert model.used == ["deep", "deep"]


def test_each_line_comes_as_its_own_playable_mp3(model, job):
    chunks = list(worker.handler(job()))

    for chunk in chunks[:-1]:
        speech = chunk["end"] - chunk["start"]
        # MP3 adds a few milliseconds of padding to each file.
        assert duration_of(base64.b64decode(chunk["audio"])) == pytest.approx(speech, abs=0.08)
    assert model.used


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
    # The lines' timings come back without their audio, which is in the upload.
    assert [sorted(c) for c in chunks[:-1]] == [["end", "id", "pause", "start"]] * 2
    assert model.used


def test_uploads_aac_when_asked_for_m4a(model, job, monkeypatch, tmp_path):
    puts = []

    class Response:
        def raise_for_status(self):
            pass

    monkeypatch.setattr(worker.requests, "put", lambda url, **kw: puts.append((url, kw)) or Response())

    chunks = list(worker.handler(job(upload_url="https://storage.example/ch1.m4a", audio_format="m4a")))

    _, kw = puts[0]
    assert kw["headers"]["Content-Type"] == "audio/mp4"
    m4a = tmp_path / "ch1.m4a"
    m4a.write_bytes(kw["data"])
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_name:format=duration", "-of", "csv=p=0", str(m4a)],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    assert probe[0] == "aac"
    # The edit list trims AAC's start-up delay, so the file is as long as the narration.
    assert float(probe[1]) == pytest.approx(chunks[-1]["duration"], abs=0.05)


def test_a_voice_the_model_lacks_is_an_error(model, job):
    bad = job()
    bad["input"]["cast"]["members"][0]["voice"] = "shallow"

    (chunk,) = worker.handler(bad)

    assert chunk == {"error": "the speech model has no voice shallow"}
    assert not model.used


def test_a_benchmark_reads_the_texts_at_each_batch_size(model):
    calls = []
    say = model.say
    model.say = lambda texts, voice: calls.append(len(texts)) or say(texts, voice)

    (chunk,) = worker.handler(
        {"input": {"benchmark": {"texts": ["One.", "Two.", "Three."], "batch_sizes": [1, 2]}, "voice": "deep"}}
    )

    assert calls == [1, 1, 1, 1, 2, 1]  # a warm-up, then 1+1+1, then 2+1
    assert [(r["batch_size"], r["audio_seconds"]) for r in chunk["runs"]] == [(1, 3.0), (2, 3.0)]
    assert duration_of(base64.b64decode(chunk["audio"][2])) == pytest.approx(3 * 1.4, abs=0.1)
