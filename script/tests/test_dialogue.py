import json
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from tta_script.cast import NARRATOR_ID, Cast, CastMember
from tta_script.dialogue import extract
from tta_script.dialogue.extract import get_text_segments, label_script
from tta_script.dialogue.types import TextSegment


HARRY_POTTER = Path(__file__).parent.parent / "evals" / "books" / "harry-potter"


@pytest.fixture(autouse=True)
def llm_labeller(monkeypatch):
    """These tests cover the LLM labeller; test_decide.py covers the default."""
    monkeypatch.setenv("TTA_LABEL_MODEL", "anthropic:claude-haiku-5-5")

CAST = Cast(
    members=[
        CastMember(id=NARRATOR_ID, names=["Narrator"], age="middle-aged", gender="male", voice="n"),
        CastMember(id="c1", names=["Bob", "Robert"], age="middle-aged", gender="male", voice="b"),
        CastMember(id="c2", names=["Mary"], age="young", gender="female", voice="m"),
    ]
)


def get_dialogue_expectation(filename: str) -> list[dict]:
    lines = (HARRY_POTTER / filename).read_text(encoding="utf-8").splitlines()
    return [
        {"speaker": speaker.strip(), "text": text.strip()}
        for speaker, text in (line.split(":", 1) for line in lines if line)
    ]


def fake_labeller(monkeypatch, speaker_for):
    """Label every segment in each batch with speaker_for(index, segment_line).
    Records each prompt and validates replies with the real response model."""
    prompts: list[str] = []

    def generate_text(_system, prompt, response_format):
        prompts.append(prompt)
        batch = prompt.split("## Text")[1].split("## Speakers")[0]
        lines = re.findall(r"^(\d+)\. (.*)$", batch, re.M)
        reply = {"dialogue": [{"index": int(i), "speaker": speaker_for(int(i), line)} for i, line in lines]}
        return response_format.model_validate(reply).model_dump_json()

    monkeypatch.setattr(extract, "generate_text", generate_text)
    return prompts


SEGMENTS = [
    TextSegment("Hello, how are you?", True, 0),
    TextSegment("asked Bob.", False, 0),
    TextSegment("Great! How about you?", True, 1),
    TextSegment("replied Mary.", False, 1),
]


def test_script_points_each_segment_at_a_cast_id(monkeypatch):
    fake_labeller(monkeypatch, lambda i, _: {0: "c1", 2: "c2"}.get(i, NARRATOR_ID))

    script = label_script(SEGMENTS, CAST)

    assert [(s.id, s.speaker_id) for s in script.segments] == [
        ("seg-0000", "c1"),
        ("seg-0001", NARRATOR_ID),
        ("seg-0002", "c2"),
        ("seg-0003", NARRATOR_ID),
    ]
    assert [s.text for s in script.segments] == [s.text for s in SEGMENTS]


def test_narration_is_always_read_by_the_narrator(monkeypatch):
    fake_labeller(monkeypatch, lambda *_: "c1")

    script = label_script(SEGMENTS, CAST)

    assert [s.speaker_id for s in script.segments] == ["c1", NARRATOR_ID, "c1", NARRATOR_ID]


def test_prompt_lists_every_name_for_each_speaker_and_breaks_paragraphs(monkeypatch):
    prompts = fake_labeller(monkeypatch, lambda *_: NARRATOR_ID)

    label_script(SEGMENTS, CAST)

    assert "- narrator: Narrator\n- c1: Bob, Robert\n- c2: Mary" in prompts[0]
    assert "1. (N) asked Bob.\n\n2. (D) Great! How about you?" in prompts[0]


def test_speaker_ids_outside_the_cast_are_rejected(monkeypatch):
    fake_labeller(monkeypatch, lambda *_: "Bob")

    with pytest.raises(ValidationError):
        label_script(SEGMENTS, CAST)


def test_later_batches_see_earlier_labels_as_context(monkeypatch):
    monkeypatch.setattr(extract, "BATCH_SIZE", 2)
    monkeypatch.setattr(extract, "CONTEXT_SIZE", 1)
    prompts = fake_labeller(monkeypatch, lambda i, _: "c1" if i == 0 else NARRATOR_ID)

    script = label_script(SEGMENTS, CAST)

    assert len(prompts) == 2
    context = prompts[1].split("## Preceding Segments")[1].split("## Text")[0]
    assert "1. (N) asked Bob. -> narrator" in context
    assert "0." not in context
    assert "(start of chapter)" in prompts[0]
    assert script.segments[0].speaker_id == "c1"


def test_labels_the_model_gives_to_context_segments_are_ignored(monkeypatch):
    monkeypatch.setattr(extract, "BATCH_SIZE", 2)

    def generate_text(_system, prompt, response_format):
        # Labels segment 0 again while labelling the batch of 2 and 3.
        indices = [0, 2, 3] if "2. (D)" in prompt else [0, 1]
        reply = {"dialogue": [{"index": i, "speaker": "c2"} for i in indices]}
        if indices == [0, 1]:
            reply["dialogue"][0]["speaker"] = "c1"
        return response_format.model_validate(reply).model_dump_json()

    monkeypatch.setattr(extract, "generate_text", generate_text)

    assert label_script(SEGMENTS, CAST).segments[0].speaker_id == "c1"


def test_unlabelled_dialogue_is_read_by_the_narrator(monkeypatch):
    def generate_text(_system, _prompt, _response_format):
        return json.dumps({"dialogue": []})

    monkeypatch.setattr(extract, "generate_text", generate_text)

    assert {s.speaker_id for s in label_script(SEGMENTS, CAST).segments} == {NARRATOR_ID}


def test_split_by_dialogue():
    result = get_text_segments((HARRY_POTTER / "01.txt").read_text(encoding="utf-8"))
    expectation = get_dialogue_expectation("01-expected.txt")
    assert [r.text for r in result] == [e["text"] for e in expectation]


def test_segments_record_their_paragraph():
    segments = get_text_segments('"Hi," said Bob. "Bye."\n\n"Hello," said Mary.')

    assert [(s.text, s.paragraph) for s in segments] == [
        ("Hi,", 0),
        ("said Bob.", 0),
        ("Bye.", 0),
        ("Hello,", 1),
        ("said Mary.", 1),
    ]


def split(text: str) -> list[tuple[str, bool]]:
    return [(s.text, s.is_dialogue) for s in get_text_segments(text)]


def test_quotes_inside_a_quote_stay_part_of_it():
    text = "“You say things are “much of a muchness”, don’t you?” said the Dormouse."

    assert split(text) == [
        ("You say things are “much of a muchness”, don’t you?", True),
        ("said the Dormouse.", False),
    ]


def test_a_quote_can_run_over_several_paragraphs():
    text = (
        "The Hatter said, “I had to sing\n\n"
        "‘Twinkle, twinkle, little bat!’\n\n"
        "You know the song?”\n\n"
        "“I do,” said Alice."
    )

    assert split(text) == [
        ("The Hatter said,", False),
        ("I had to sing", True),
        ("‘Twinkle, twinkle, little bat!’", True),
        ("You know the song?", True),
        ("I do,", True),
        ("said Alice.", False),
    ]


def test_a_speech_continues_when_the_next_paragraph_reopens_the_quote():
    text = '"It was a long speech.\n\n"And it went on," said Bob.'

    assert split(text) == [
        ("It was a long speech.", True),
        ("And it went on,", True),
        ("said Bob.", False),
    ]


def test_an_unclosed_quote_does_not_turn_the_next_paragraphs_into_dialogue():
    text = '"Is that all right, he asked.\n\nThey left.\n\n"Yes," said Bob.'

    assert split(text) == [
        ("Is that all right, he asked.", True),
        ("They left.", False),
        ("Yes,", True),
        ("said Bob.", False),
    ]


def test_a_paragraph_that_lost_its_opening_quote_starts_in_dialogue():
    assert split('I had a dream," said Harry. "It was flying."') == [
        ("I had a dream,", True),
        ("said Harry.", False),
        ("It was flying.", True),
    ]


def test_wrapped_lines_join_into_one_paragraph():
    assert split('"Hello\nthere," said\n  Bob.') == [("Hello there,", True), ("said Bob.", False)]


ATTRIBUTED = [
    TextSegment("This is no resemblance,", True, 0),
    TextSegment("said he.", False, 0),
    TextSegment("You think it a faithful portrait.", True, 0),
]


def test_quotes_around_a_short_attribution_get_one_speaker(monkeypatch):
    fake_labeller(monkeypatch, lambda i, _: {0: "c1", 2: "c2"}.get(i, NARRATOR_ID))

    script = label_script(ATTRIBUTED, CAST)

    assert [s.speaker_id for s in script.segments] == ["c1", NARRATOR_ID, "c1"]


def test_the_more_confident_label_wins_across_an_attribution(monkeypatch):
    monkeypatch.setattr(
        extract, "decide_speakers", lambda *_: ({0: "c1", 2: "c2"}, {0: 0.55, 2: 0.9})
    )
    monkeypatch.setenv("TTA_LABEL_MODEL", "openai-decisions:gpt-6-luna")

    script = label_script(ATTRIBUTED, CAST)

    assert [(s.speaker_id, s.confidence) for s in script.segments] == [
        ("c2", 0.9),
        (NARRATOR_ID, None),
        ("c2", 0.9),
    ]


def test_narrator_labels_and_long_narration_are_left_alone(monkeypatch):
    segments = [
        TextSegment("Hi,", True, 0),
        TextSegment("began Bob, but Mary cut in with a decided,", False, 0),
        TextSegment("No!", True, 0),
        TextSegment("She didn't say", False, 1),
        TextSegment("never", True, 1),
        TextSegment("but", False, 1),
        TextSegment("Bye.", True, 1),
    ]
    labels = {0: "c1", 2: "c2", 4: NARRATOR_ID, 6: "c2"}
    fake_labeller(monkeypatch, lambda i, _: labels.get(i, NARRATOR_ID))

    script = label_script(segments, CAST)

    assert [script.segments[i].speaker_id for i in (0, 2, 4, 6)] == ["c1", "c2", NARRATOR_ID, "c2"]


def test_single_quotes_mark_dialogue_in_british_style_text():
    text = (
        "‘I’m goin’ home,’ says he, ‘an’ you’ll not stop me.’\n\n"
        "They called him a ‘true sea-dog’ and a ‘real old salt’.\n\n"
        "‘He said “no” to me,’ said Jim."
    )

    assert split(text) == [
        ("I’m goin’ home,", True),
        ("says he,", False),
        ("an’ you’ll not stop me.", True),
        ("They called him a", False),
        ("true sea-dog", True),
        ("and a", False),
        ("real old salt", True),
        (".", False),
        ("He said “no” to me,", True),
        ("said Jim.", False),
    ]


def test_straight_single_quotes_tell_apostrophes_from_quotes():
    text = (
        "'It's late,' said Bob, ''tis very late.'\n\n"
        "Crinkle, crinkle, 'ittle 'tar, she sang.\n\n"
        "'Yes,' said Mary. 'Go on."
    )

    assert split(text) == [
        ("It's late,", True),
        ("said Bob,", False),
        ("'tis very late.", True),
        ("Crinkle, crinkle, 'ittle 'tar, she sang.", False),
        ("Yes,", True),
        ("said Mary.", False),
        ("Go on.", True),
    ]


def test_apostrophes_in_double_quote_text_are_not_dialogue():
    assert split("\"'Scuse me,\" said the owner. They'd come in 'cause of the rain.") == [
        ("'Scuse me,", True),
        ("said the owner. They'd come in 'cause of the rain.", False),
    ]
