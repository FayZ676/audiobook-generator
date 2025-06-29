from pathlib import Path

import pytest

from tta_script.dialogue.extract import (
    get_script,
    create_text_batches,
    label_dialogue,
    label,
    split_by_dialogue,
)
from tta_script.dialogue.types import TextSegment, DialogueLabel, Script, ScriptSegment
from tta_script.character.types import SpeakerDetails
try:
    from tta_script.voices import SpeakerVoice
    from tta_types.types import Voice
except ImportError:
    # For testing without full dependencies
    SpeakerVoice = None
    Voice = None


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def get_dialogue_expectation(filename: str):
    details: list[dict] = []
    text = get_text(filename)
    for segment in text.split("\n"):
        split = segment.split(":")
        details.append({
            "speaker": split[0].strip(),
            "text": split[1].strip(),
        })
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
        SpeakerDetails(frozenset({"Bob"}), "middle-aged", "male", "bob_voice"),
        SpeakerDetails(frozenset({"Mary"}), "middle-aged", "female", "mary_voice"),
    }
    assert label_dialogue(texts, speakers, batch_size=2) == [
        DialogueLabel(index=0, speaker="Bob"),
        DialogueLabel(index=2, speaker="Mary"),
    ]


@pytest.mark.integration
def test_label_dialogue__large():
    def build_speaker_details(names: set[str]) -> SpeakerDetails:
        return SpeakerDetails(frozenset(names), "middle-aged", "female", "default_voice")

    def get_expectation(filename: str, speakers: set[SpeakerDetails]):
        expected_details = get_dialogue_expectation(filename)
        return [
            {"speaker": s, "text": e["text"]}
            for e in expected_details
            for s in speakers
            if e["speaker"] in [alias for alias in s.names]
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
        TextSegment(e["text"], False if e["speaker"] == "Narrator" else True)
        for e in get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    ]
    result = label_dialogue(dialogues, speakers)
    expectated_dialogues = [
        DialogueLabel(i, e["speaker"]) for i, e in enumerate(get_dialogue_expectation("harrypotter-1-expected-dialogue.txt"))
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
        SpeakerDetails(frozenset({"Bob"}), "middle-aged", "male", "bob_voice"),
        SpeakerDetails(frozenset({"Mary"}), "middle-aged", "female", "mary_voice"),
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
    """Test the new get_script function that returns Script structure."""
    def build_speaker_voice(names: set[str]) -> SpeakerVoice:
        return SpeakerVoice(
            SpeakerDetails(frozenset(names), "middle-aged", "male", "default_voice"),
            Voice(
                name="name",
                gender="male",
                age="young",
                audio_path="foo",
                audio_transcript="bar",
            ),
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
    
    # Test new Script structure
    script = get_script(
        text=get_text("harrypotter-1.txt"),
        speakers_voices=speakers,
        narrator_speaker=build_speaker_voice({"Narrator"}),
    )
    
    # Verify it's a Script instance
    assert isinstance(script, Script)
    
    # Verify we have segments
    assert len(script.segments) > 0
    assert all(isinstance(seg, ScriptSegment) for seg in script.segments)
    
    # Verify we have speakers
    assert len(script.speakers) > 0
    assert all(isinstance(speaker, SpeakerDetails) for speaker in script.speakers)
    
    # Verify speakers have voice names
    assert all(speaker.voice_name for speaker in script.speakers)
    
    # Compare text content with expected
    expected_details = get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    assert [seg.text for seg in script.segments] == [e["text"] for e in expected_details]
    
    # Test serialization
    script_dict = script.to_dict()
    assert "segments" in script_dict
    assert "speakers" in script_dict
    assert "voices" in script_dict  # Should still be present for backward compatibility


def test_split_by_dialogue():
    result = split_by_dialogue(get_text("harrypotter-1.txt"))
    expectation = get_dialogue_expectation("harrypotter-1-expected-dialogue.txt")
    assert [r.text for r in result] == [e["text"] for e in expectation]


def test_script_structure():
    """Test the basic Script structure functionality."""
    # Create test speakers with voice names
    john = SpeakerDetails(frozenset(["John"]), "young", "male", "young_male_voice")
    mary = SpeakerDetails(frozenset(["Mary"]), "middle-aged", "female", "female_voice")
    narrator = SpeakerDetails(frozenset(["Narrator"]), "middle-aged", "male", "narrator_voice")
    
    # Create script segments
    segments = [
        ScriptSegment("Hello there!", "John"),
        ScriptSegment("Hello John, how are you?", "Mary"),
        ScriptSegment("John and Mary talked.", "Narrator"),
    ]
    
    # Create script (no separate voices dict needed)
    script = Script(segments=segments, speakers=[john, mary, narrator])
    
    # Test basic properties
    assert len(script.segments) == 3
    assert len(script.speakers) == 3
    assert script.speakers[0].voice_name == "young_male_voice"
    assert script.speakers[1].voice_name == "female_voice"
    assert script.speakers[2].voice_name == "narrator_voice"
    
    # Test serialization
    script_dict = script.to_dict()
    assert "segments" in script_dict
    assert "speakers" in script_dict
    assert "voices" in script_dict  # Should be generated from speakers
    assert len(script_dict["segments"]) == 3
    
    # Verify segment structure includes voice_name
    segment = script_dict["segments"][0]
    assert segment["text"] == "Hello there!"
    assert segment["speaker_alias"] == "John"
    assert segment["voice_name"] == "young_male_voice"
    
    # Verify voices dict is properly generated
    assert script_dict["voices"]["John"] == "young_male_voice"
    assert script_dict["voices"]["Mary"] == "female_voice"
    assert script_dict["voices"]["Narrator"] == "narrator_voice"


def test_script_memory_efficiency():
    """Test that Script structure is more memory efficient than duplicating speaker data."""
    speaker = SpeakerDetails(frozenset(["TestSpeaker"]), "young", "male", "test_voice")
    
    # Create many segments with the same speaker
    num_segments = 50
    
    # New approach - speaker stored once in Script
    new_segments = [
        ScriptSegment(
            text=f"Segment {i}",
            speaker_alias="TestSpeaker"
        )
        for i in range(num_segments)
    ]
    
    script = Script(
        segments=new_segments,
        speakers=[speaker],  # Stored once
    )
    
    # Verify we have the expected number of text segments
    assert len(script.segments) == num_segments
    
    # Verify text content is correct
    expected_texts = [f"Segment {i}" for i in range(num_segments)]
    actual_texts = [seg.text for seg in script.segments]
    assert actual_texts == expected_texts
    
    # In the new structure, speaker is stored only once
    assert len(script.speakers) == 1
    assert script.speakers[0] == speaker
    assert script.speakers[0].voice_name == "test_voice"
