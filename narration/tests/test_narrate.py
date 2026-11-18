import numpy as np
import pytest

from tta_narration.narrate import PARAGRAPH_GAP_S, PIECE_GAP_S, VoiceClip, narrate
from tta_script.cast import NARRATOR_ID, Cast, CastMember
from tta_script.script import Script, ScriptSegment

SR = 100
CAST = Cast(
    members=[
        CastMember(id=NARRATOR_ID, names=["Narrator"], age="middle-aged", gender="male", voice="deep"),
        CastMember(id="c1", names=["Alice"], age="young", gender="female", voice="bright"),
        CastMember(id="c2", names=["the Rabbit"], age="old", gender="male"),
    ]
)
VOICES = {"deep": VoiceClip("deep.wav", "Hello."), "bright": VoiceClip("bright.wav", "Hi.")}


class FakeSpeaker:
    """One second of audio per text; remembers what it was asked to read."""

    sample_rate = SR

    def __init__(self):
        self.calls = []

    def say(self, texts, voice):
        self.calls.append((voice, texts))
        return [np.ones(SR, dtype=np.float32) for _ in texts]


def line(i, text, speaker, paragraph):
    return ScriptSegment(id=f"seg-{i}", text=text, speaker_id=speaker, paragraph=paragraph)


def test_each_voice_reads_its_lines_in_one_request():
    script = Script(
        segments=[
            line(0, "Alice sat down.", NARRATOR_ID, 0),
            line(1, "What a day,", "c1", 1),
            line(2, "said Alice.", NARRATOR_ID, 1),
        ]
    )
    speaker = FakeSpeaker()

    narrate(script, CAST, VOICES, speaker)

    assert speaker.calls == [
        (VOICES["deep"], ["Alice sat down.", "said Alice."]),
        (VOICES["bright"], ["What a day,"]),
    ]


def test_lines_are_timed_with_a_longer_pause_between_paragraphs():
    script = Script(
        segments=[
            line(0, "Alice sat down.", NARRATOR_ID, 0),
            line(1, "What a day,", "c1", 1),
            line(2, "said Alice.", NARRATOR_ID, 1),
        ]
    )

    narration = narrate(script, CAST, VOICES, FakeSpeaker())

    after_first = 1 + PARAGRAPH_GAP_S
    assert [(t.id, t.start, t.end) for t in narration.lines] == [
        ("seg-0", 0, 1),
        ("seg-1", after_first, after_first + 1),
        ("seg-2", after_first + 1 + PIECE_GAP_S, after_first + 2 + PIECE_GAP_S),
    ]
    assert narration.duration == pytest.approx(narration.lines[-1].end)


def test_long_lines_are_read_in_pieces_and_quotes_straightened():
    sentence = "The " + "very " * 25 + "long day ended."
    script = Script(segments=[line(0, f"{sentence} “{sentence}”", NARRATOR_ID, 0)])
    speaker = FakeSpeaker()

    narration = narrate(script, CAST, VOICES, speaker)

    assert speaker.calls[0][1] == [sentence, f'"{sentence}"']
    assert narration.lines[0].end == pytest.approx(2 + PIECE_GAP_S)


def test_blank_lines_are_skipped():
    script = Script(segments=[line(0, "  ", NARRATOR_ID, 0), line(1, "Hi.", NARRATOR_ID, 0)])

    assert [t.id for t in narrate(script, CAST, VOICES, FakeSpeaker()).lines] == ["seg-1"]


def test_missing_voices_are_all_named_before_anything_is_read():
    script = Script(segments=[line(0, "Late!", "c2", 0), line(1, "Hi.", "c1", 0)])
    speaker = FakeSpeaker()

    with pytest.raises(ValueError, match="no voice for the Rabbit; no clip for voices bright"):
        narrate(script, CAST, {"deep": VOICES["deep"]}, speaker)
    assert not speaker.calls
