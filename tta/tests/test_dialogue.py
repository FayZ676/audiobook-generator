from pathlib import Path

import pytest

from tta.dialogue.extract import (
    get_dialogue_details,
    create_text_batches,
    label_dialogue,
    label,
    split_by_dialogue,
)
from tta.dialogue.types import TextSegment, DialogueLabel, DialogueDetails
from tta.character.types import SpeakerDetails
from tta.voices import SpeakerVoice, Voice


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def get_dialogue_expectation(filename: str):
    details: list[DialogueDetails] = []
    text = get_text(filename)
    for segment in text.split("\n"):
        split = segment.split(":")
        details.append(
            DialogueDetails(
                SpeakerDetails(frozenset({split[0].strip()}), "middle-aged", "female"),
                split[1].strip(),
                "foo",
            )
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
        SpeakerDetails(frozenset({"Bob"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Mary"}), "middle-aged", "female"),
    }
    assert label_dialogue(texts, speakers, batch_size=2) == [
        DialogueLabel(index=0, speaker="Bob"),
        DialogueLabel(index=2, speaker="Mary"),
    ]


@pytest.mark.integration
def test_label_dialogue__large():
    def build_speaker_details(names: set[str]) -> SpeakerDetails:
        return SpeakerDetails(frozenset(names), "middle-aged", "female")

    def get_expectation(filename: str, speakers: set[SpeakerDetails]):
        return [
            DialogueDetails(s, e.text, "foo")
            for e in get_dialogue_expectation(filename)
            for s in speakers
            if e.speaker.names.issubset(s.names)
        ]

    speakers = {
        build_speaker_details({"Narrator"}),
        build_speaker_details({"Professor McGonagall"}),
        build_speaker_details({"Albus Dumbledore"}),
        build_speaker_details({"Mrs. Dursley", "Aunt Petunia"}),
        build_speaker_details({"Mr. Dursley", "Uncle Vernon"}),
        build_speaker_details({"Hagrid"}),
        build_speaker_details({"Dudley"}),
        build_speaker_details({"Harry Potter"}),
    }
    expectation = get_expectation("harrypotter-1-expected-dialogue.txt", speakers)
    dialogues = [
        TextSegment(e.text, False if e.speaker == "Narrator" else True)
        for e in expectation
    ]
    result = label_dialogue(dialogues, speakers)
    expectated_dialogues = [
        DialogueLabel(i, ", ".join(e.speaker.names)) for i, e in enumerate(expectation)
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
        SpeakerDetails(frozenset({"Bob"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Mary"}), "middle-aged", "female"),
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
def test_get_dialogue_details():
    def build_speaker_voice(names: set[str]) -> SpeakerVoice:
        return SpeakerVoice(
            SpeakerDetails(frozenset(names), "middle-aged", "male"),
            Voice("name", "male", "young", "foo", "bar"),
        )

    speakers = {
        build_speaker_voice({"Professor McGonagall"}),
        build_speaker_voice({"Albus Dumbledore"}),
        build_speaker_voice({"Mrs. Dursley", "Aunt Petunia"}),
        build_speaker_voice({"Mr. Dursley", "Uncle Vernon"}),
        build_speaker_voice({"Hagrid"}),
        build_speaker_voice({"Dudley"}),
        build_speaker_voice({"Harry Potter"}),
    }
    result = get_dialogue_details(get_text("harrypotter-1.txt"), speakers)
    expectation = get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    assert [r.text for r in result] == [e.text for e in expectation]


def test_split_by_dialogue():
    result = split_by_dialogue(get_text("harrypotter-1.txt"))
    expectation = get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    assert [r.text for r in result] == [e.text for e in expectation]
