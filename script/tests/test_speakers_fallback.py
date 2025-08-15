"""Tests for the fallback behavior in speakers.py"""

import pytest

from tta_types.types import Voice, Character, Speaker
from tta_script.speakers import get_speakers


def test_get_speakers_uses_narrator_fallback_when_no_matching_voice():
    """Test that characters use Narrator voice when no matching voice is found"""
    characters = {
        Character(names=["OldLady"], age="old", gender="female"),
    }
    
    voices = [
        Voice(name="Narrator", age="middle-aged", gender="male", 
              audio_path="narrator.wav", audio_transcript="test"),
        Voice(name="YoungMale", age="young", gender="male", 
              audio_path="voice1.wav", audio_transcript="test"),
    ]
    
    previous_speakers = set()
    
    result = get_speakers(characters, voices, previous_speakers)
    
    assert len(result) == 1
    speaker = next(iter(result))
    assert speaker.character.first_alias() == "OldLady"
    assert speaker.voice.name == "Narrator"


def test_get_speakers_succeeds_with_more_characters_than_voices():
    """Test that having more characters than voices doesn't raise an exception"""
    characters = {
        Character(names=["Alice"], age="young", gender="female"),
        Character(names=["Bob"], age="middle-aged", gender="male"),
        Character(names=["Charlie"], age="old", gender="male"),
    }
    
    voices = [
        Voice(name="Narrator", age="middle-aged", gender="male", 
              audio_path="narrator.wav", audio_transcript="test"),
        Voice(name="Voice1", age="young", gender="female", 
              audio_path="voice1.wav", audio_transcript="test"),
    ]
    
    previous_speakers = set()
    
    result = get_speakers(characters, voices, previous_speakers)
    
    assert len(result) == 3
    
    # Alice should get Voice1 (perfect match)
    alice_speaker = next(s for s in result if s.character.first_alias() == "Alice")
    assert alice_speaker.voice.name == "Voice1"
    
    # Bob should get Narrator (perfect match) 
    bob_speaker = next(s for s in result if s.character.first_alias() == "Bob")
    assert bob_speaker.voice.name == "Narrator"
    
    # Charlie should get Narrator (fallback)
    charlie_speaker = next(s for s in result if s.character.first_alias() == "Charlie")
    assert charlie_speaker.voice.name == "Narrator"


def test_get_speakers_raises_error_when_no_narrator_voice():
    """Test that an error is still raised when no Narrator voice is available"""
    characters = {
        Character(names=["OldLady"], age="old", gender="female"),
    }
    
    voices = [
        Voice(name="YoungMale", age="young", gender="male", 
              audio_path="voice1.wav", audio_transcript="test"),
    ]
    
    previous_speakers = set()
    
    with pytest.raises(ValueError, match="no Narrator voice found"):
        get_speakers(characters, voices, previous_speakers)


def test_get_speakers_prefers_matching_voice_over_narrator():
    """Test that characters still get matching voices when available"""
    characters = {
        Character(names=["YoungGirl"], age="young", gender="female"),
    }
    
    voices = [
        Voice(name="Narrator", age="middle-aged", gender="male", 
              audio_path="narrator.wav", audio_transcript="test"),
        Voice(name="MatchingVoice", age="young", gender="female", 
              audio_path="matching.wav", audio_transcript="test"),
    ]
    
    previous_speakers = set()
    
    result = get_speakers(characters, voices, previous_speakers)
    
    assert len(result) == 1
    speaker = next(iter(result))
    assert speaker.character.first_alias() == "YoungGirl"
    assert speaker.voice.name == "MatchingVoice"