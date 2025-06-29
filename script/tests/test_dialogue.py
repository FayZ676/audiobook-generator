from pathlib import Path

import pytest

from tta_script.dialogue.extract import (
    get_script,
    create_text_batches,
    label_dialogue,
    label,
    split_by_dialogue,
)
from tta_script.dialogue.types import TextSegment, DialogueLabel
from tta_script.character.types import SpeakerDetails, Age, Gender
from tta_script.voices import Speaker
from tta_types.types import Voice


def build_speaker_voice(
    names: set[str],
    gender: Gender = "male",
    age: Age = "middle-aged",
    voice_name: str = "default_voice",
    audio_path: str = "foo",
    audio_transcript: str = "foo",
):
    return Speaker(
        SpeakerDetails(frozenset(names), age, gender),
        Voice(
            name=voice_name,
            age=age,
            gender=gender,
            audio_path=audio_path,
            audio_transcript=audio_transcript,
        ),
    )


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def get_dialogue_expectation(filename: str):
    details: list[dict] = []
    text = get_text(filename)
    for segment in text.split("\n"):
        split = segment.split(":")
        details.append(
            {
                "speaker": split[0].strip(),
                "text": split[1].strip(),
            }
        )
    return details


@pytest.mark.integration
def test_label_dialogue():
    texts = [
        TextSegment("Hello, how are you?", True),
        TextSegment("asked Bob.", False),
        TextSegment("Great! How about you?", True),
        TextSegment("replied Mary.", False),
    ]
    speakers = {
        build_speaker_voice({"Bob"}, gender="male", voice_name="bob_voice"),
        build_speaker_voice({"Mary"}, gender="female", voice_name="mary_voice"),
    }
    assert label_dialogue(texts, speakers, batch_size=2) == [
        DialogueLabel(index=0, speaker="Bob"),
        DialogueLabel(index=2, speaker="Mary"),
    ]


@pytest.mark.integration
def test_label_dialogue__large():
    speakers = {
        build_speaker_voice({"Narrator"}, age="middle-aged", gender="male"),
        build_speaker_voice({"Professor McGonagall"}, age="old", gender="female"),
        build_speaker_voice({"Albus Dumbledore"}, age="old", gender="male"),
        build_speaker_voice(
            {"Mrs. Dursley", "Aunt Petunia"}, age="middle-aged", gender="female"
        ),
        build_speaker_voice(
            {"Mr. Dursley", "Uncle Vernon"}, age="middle-aged", gender="male"
        ),
        build_speaker_voice({"Hagrid"}, age="middle-aged", gender="male"),
        build_speaker_voice({"Dudley"}, age="young", gender="male"),
        build_speaker_voice({"Harry Potter"}, age="young", gender="male"),
    }
    dialogues = [
        TextSegment(e["text"], False if e["speaker"] == "Narrator" else True)
        for e in get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    ]
    result = label_dialogue(dialogues, speakers)
    expectated_dialogues = [
        DialogueLabel(i, e["speaker"])
        for i, e in enumerate(
            get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
        )
    ]

    failures = []
    for r, e in zip(result, expectated_dialogues):
        if r.index == e.index and r.speaker in e.speaker:
            continue
        failures.append(f"({r.index}) Expected any of {e.speaker} but got {r.speaker}")
    assert len(failures) == 0, "\n".join(failures)


@pytest.mark.integration
def test_label():
    dialogues = {
        0: TextSegment("Hello, how are you?", True),
        1: TextSegment("asked Bob.", False),
        2: TextSegment("Great! How about you?", True),
        3: TextSegment("replied Mary.", False),
    }
    speakers = {
        build_speaker_voice({"Bob"}, gender="male", voice_name="bob_voice"),
        build_speaker_voice({"Mary"}, gender="female", voice_name="mary_voice"),
    }
    assert label(dialogues, speakers) == [
        DialogueLabel(index=0, speaker="Bob"),
        DialogueLabel(index=2, speaker="Mary"),
    ]


def test_create_text_batches():
    texts = [
        TextSegment("Hello, how are you?", True),
        TextSegment("asked Bob.", False),
        TextSegment("Great! How about you?", True),
        TextSegment("replied Mary.", False),
    ]
    expected_batches = [
        {
            0: TextSegment("Hello, how are you?", True),
            1: TextSegment("asked Bob.", False),
        },
        {
            2: TextSegment("Great! How about you?", True),
            3: TextSegment("replied Mary.", False),
        },
    ]
    assert create_text_batches(texts, 2) == expected_batches


@pytest.mark.integration
def test_get_script():
    """Test the get_script function that returns Script structure."""

    speakers = {
        build_speaker_voice({"Professor McGonagall"}),
        build_speaker_voice({"Albus Dumbledore"}),
        build_speaker_voice({"Mrs. Dursley", "Aunt Petunia"}),
        build_speaker_voice({"Mr. Dursley", "Uncle Vernon"}),
        build_speaker_voice({"Hagrid"}),
        build_speaker_voice({"Dudley"}),
        build_speaker_voice({"Harry Potter"}),
    }

    script = get_script(
        text=get_text("harrypotter-1.txt"),
        speakers_voices=speakers,
        narrator_speaker=build_speaker_voice({"Narrator"}),
    )

    expected_details = get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    assert [seg.text for seg in script.segments] == [
        e["text"] for e in expected_details
    ]


def test_split_by_dialogue():
    result = split_by_dialogue(get_text("harrypotter-1.txt"))
    expectation = get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    assert [r.text for r in result] == [e["text"] for e in expectation]
