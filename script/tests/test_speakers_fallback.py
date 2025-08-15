"""Tests for the fallback behavior in speakers.py"""

import pytest

from tta_types.types import Voice, Character, Speaker
from tta_script.speakers import get_speakers


### Test Voices
narrator = Voice(
    name="Narrator",
    age="middle-aged",
    gender="male",
    audio_path="narrator.wav",
    audio_transcript="test",
)
young_male = Voice(
    name="YoungMale",
    age="young",
    gender="male",
    audio_path="voice1.wav",
    audio_transcript="test",
)
young_female = Voice(
    name="YoungFemale",
    age="young",
    gender="female",
    audio_path="voice2.wav",
    audio_transcript="test",
)


### Test Characters
old_lady = Character(names=["OldLady"], age="old", gender="female")
alice = Character(names=["Alice"], age="young", gender="female")
emma = Character(names=["Emma"], age="young", gender="female")
bob = Character(names=["Bob"], age="middle-aged", gender="male")
charlie = Character(names=["Charlie"], age="old", gender="male")


def build_speaker(character: Character, voice: Voice) -> Speaker:
    """Helper function to build a Speaker object."""
    return Speaker(character=character, voice=voice)


def test_get_speakers_uses_narrator_fallback_when_no_matching_voice():
    """Test that characters use Narrator voice when no matching voice is found"""
    characters = {old_lady}
    voices = [narrator, young_male]

    result = get_speakers(characters, voices, set())
    expected = {build_speaker(old_lady, narrator)}
    assert result == expected


def test_get_speakers_succeeds_with_more_characters_than_voices():
    """Test that having more characters than voices doesn't raise an exception"""
    characters = {alice, bob, charlie}
    voices = [narrator, young_male]

    result = get_speakers(characters, voices, set())
    expected = {
        build_speaker(alice, narrator),
        build_speaker(bob, narrator),
        build_speaker(charlie, narrator),
    }
    assert result == expected


def test_get_speakers_raises_error_when_no_narrator_voice():
    """Test that an error is still raised when no Narrator voice is available"""
    characters = {old_lady}
    voices = [young_male]

    with pytest.raises(ValueError, match="no Narrator voice found"):
        get_speakers(characters, voices, set())


def test_get_speakers_prefers_matching_voice_over_narrator():
    """Test that characters still get matching voices when available"""
    characters = {alice}
    voices = [narrator, young_female]

    result = get_speakers(characters, voices, set())
    expected = {build_speaker(alice, young_female)}
    assert result == expected


def test_get_speakers_assigns_one_voice_per_character_with_narrator_fallback():
    """Test that when multiple characters match one voice, one gets the voice and others get narrator"""
    characters = {alice, emma}
    voices = [narrator, young_female]

    result = get_speakers(characters, voices, set())
    narrator_speakers = [s for s in result if s.voice.name == "Narrator"]
    young_female_speakers = [s for s in result if s.voice.name == "YoungFemale"]
    assert len(narrator_speakers) == 1
    assert len(young_female_speakers) == 1
