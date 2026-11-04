import pytest

from tta_types.cast import NARRATOR_ID, Cast, CastMember
from tta_types.script import Script, ScriptSegment


def member(member_id: str, voice: str = "v") -> CastMember:
    return CastMember(id=member_id, names=[member_id], age="young", gender="male", voice=voice)


def test_next_id_starts_at_c1_and_skips_non_numbered_ids():
    assert Cast().next_id() == "c1"
    assert Cast(members=[member(NARRATOR_ID), member("c2"), member("c10")]).next_id() == "c11"


def test_speech_segments_use_each_speakers_voice():
    cast = Cast(members=[member(NARRATOR_ID, "narrator-voice"), member("c1", "bob-voice")])
    script = Script(
        segments=[
            ScriptSegment(id="seg-0000", text="Hi", speaker_id="c1"),
            ScriptSegment(id="seg-0001", text="said Bob.", speaker_id=NARRATOR_ID),
        ]
    )

    assert [(s.id, s.voice_name) for s in script.to_speech_segments(cast)] == [
        ("seg-0000", "bob-voice"),
        ("seg-0001", "narrator-voice"),
    ]


def test_speech_segments_reject_unknown_speakers():
    script = Script(segments=[ScriptSegment(id="seg-0000", text="Hi", speaker_id="c9")])

    with pytest.raises(ValueError, match="unknown speaker 'c9'"):
        script.to_speech_segments(Cast(members=[member(NARRATOR_ID)]))
