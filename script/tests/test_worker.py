from tta_script import worker
from tta_script.cast import NARRATOR_ID, Cast, CastMember
from tta_script.script import Script, ScriptSegment

CAST = Cast(members=[CastMember(id=NARRATOR_ID, names=["Narrator"], age="middle-aged", gender="male")])
SCRIPT = Script(segments=[ScriptSegment(id="seg-0", text="Hi", speaker_id=NARRATOR_ID, is_dialogue=True)])


def test_build_returns_the_script_and_the_updated_cast(monkeypatch):
    calls = []

    def build_script(text, cast, voices):
        calls.append((text, cast, voices))
        return SCRIPT, CAST

    monkeypatch.setattr(worker, "build_script", build_script)

    out = worker.handler(
        {"input": {"task": "build", "text": "Hi", "voices": [{"name": "v1", "age": "old", "gender": "female"}]}}
    )

    assert out == {"script": SCRIPT.model_dump(), "cast": CAST.model_dump()}
    text, cast, voices = calls[0]
    assert text == "Hi" and cast == Cast() and voices[0].name == "v1"


def test_recheck_returns_a_speaker_per_segment(monkeypatch):
    monkeypatch.setattr(worker, "recheck_segments", lambda script, cast, ids: {i: "c1" for i in ids})

    out = worker.handler(
        {"input": {"task": "recheck", "script": SCRIPT.model_dump(), "cast": CAST.model_dump(), "segment_ids": ["seg-0"]}}
    )

    assert out == {"speakers": {"seg-0": "c1"}}


def test_wrong_input_is_an_error_not_a_crash():
    assert "error" in worker.handler({"input": {"task": "build"}})
    assert "error" in worker.handler({"input": {"task": "narrate", "text": "Hi"}})
