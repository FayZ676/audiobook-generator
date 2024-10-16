import pytest
from tta.voices import Voice, voices_catalogue  # Use relative imports
from tta.character import Character  # Use relative imports
from tta.character_voice_mapping import map_characters_to_voices, CharacterVoiced

# Sample character data for testing
@pytest.fixture
def characters():
    return [
        Character(name="Alice", age="young-adult", gender="female"),
        Character(name="Bob", age="middle-aged", gender="male"),
        Character(name="Charlie", age="child", gender="male"),
    ]

# Test the mapping of characters to voices
def test_map_characters_to_voices(characters):
    voiced_characters = map_characters_to_voices(characters)

    # Check if the length of voiced_characters matches the input characters
    assert len(voiced_characters) == len(characters)

    # Verify the assigned voices
    for voiced in voiced_characters:
        assert voiced.character in characters
        assert voiced.voice.age_group == voiced.character.age
        assert voiced.voice.gender == voiced.character.gender

# Test case for when there are not enough voices
def test_no_available_voice_for_character():
    # Create a character that does not match any available voices
    characters = [Character(name="Unknown", age="elderly", gender="non-binary")]

    with pytest.raises(ValueError, match="No available voices for Unknown with age elderly and gender non-binary"):
        map_characters_to_voices(characters)

# Test case to ensure that all voices are assigned only once
def test_voice_uniqueness():
    characters = [
        Character(name="Alice", age="young-adult", gender="female"),
        Character(name="Bob", age="young-adult", gender="male"),
        Character(name="Charlie", age="middle-aged", gender="male"),
    ]

    voiced_characters = map_characters_to_voices(characters)

    # Collect assigned voices
    assigned_voices = {voiced.voice.id for voiced in voiced_characters}

    # Ensure all voices are unique
    assert len(assigned_voices) == len(voiced_characters)