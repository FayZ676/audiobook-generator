import numpy as np
import pytest

from tta_narration.narrate import PARAGRAPH_GAP_S, PIECE_GAP_S, narrate
from tta_narration.speech import SpeechModel, VoiceClip
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


class FakeModel(SpeechModel):
    """One second of audio per text; remembers what it was asked to read."""

    sample_rate = SR

    def __init__(self):
        self.calls = []

    def say(self, texts, voice):
        self.calls.append((voice, texts))
        return [np.ones(SR, dtype=np.float32) for _ in texts]


def line(i, text, speaker, paragraph):
    return ScriptSegment(id=f"seg-{i}", text=text, speaker_id=speaker, paragraph=paragraph)


SCRIPT = Script(
    segments=[
        line(0, "Alice sat down.", NARRATOR_ID, 0),
        line(1, "What a day,", "c1", 1),
        line(2, "said Alice.", NARRATOR_ID, 1),
    ]
)


def test_lines_are_read_in_order_one_request_each():
    model = FakeModel()

    list(narrate(SCRIPT, CAST, VOICES, model))

    assert model.calls == [
        (VOICES["deep"], ["Alice sat down."]),
        (VOICES["bright"], ["What a day,"]),
        (VOICES["deep"], ["said Alice."]),
    ]


def test_each_line_comes_as_soon_as_it_is_read():
    model = FakeModel()

    lines = narrate(SCRIPT, CAST, VOICES, model)
    first = next(lines)

    assert first.id == "seg-0" and len(model.calls) == 1


def test_lines_are_timed_with_a_longer_pause_between_paragraphs():
    lines = list(narrate(SCRIPT, CAST, VOICES, FakeModel()))

    after_first = 1 + PARAGRAPH_GAP_S
    assert [(t.id, t.start, t.end) for t in lines] == [
        ("seg-0", 0, 1),
        ("seg-1", after_first, after_first + 1),
        ("seg-2", after_first + 1 + PIECE_GAP_S, after_first + 2 + PIECE_GAP_S),
    ]
    # Each line's audio is its pause and speech, so the lines join end to end.
    assert sum(len(t.audio) for t in lines) == pytest.approx(lines[-1].end * SR)


def test_long_lines_are_read_in_pieces_and_quotes_straightened():
    sentence = "The " + "very " * 25 + "long day ended."
    script = Script(segments=[line(0, f"{sentence} “{sentence}”", NARRATOR_ID, 0)])
    model = FakeModel()

    (read,) = narrate(script, CAST, VOICES, model)

    assert model.calls[0][1] == [sentence, f'"{sentence}"']
    assert read.end == pytest.approx(2 + PIECE_GAP_S)


def test_blank_lines_are_skipped():
    script = Script(segments=[line(0, "  ", NARRATOR_ID, 0), line(1, "Hi.", NARRATOR_ID, 0)])

    assert [t.id for t in narrate(script, CAST, VOICES, FakeModel())] == ["seg-1"]


def test_missing_voices_are_all_named_before_anything_is_read():
    script = Script(segments=[line(0, "Late!", "c2", 0), line(1, "Hi.", "c1", 0)])
    model = FakeModel()

    with pytest.raises(ValueError, match="no voice for the Rabbit; no clip for voices bright"):
        narrate(script, CAST, {"deep": VOICES["deep"]}, model)
    assert not model.calls
