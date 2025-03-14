from tta.character.types import Character
from tta.voices import get_voices


def test_map_characters_to_voices():
    """Test the mapping of characters to voices ensuring all voices are unique"""

    characters = {
        Character(name="Alice", age="middle-aged", gender="female"),
        Character(name="Gwen", age="middle-aged", gender="female"),
        Character(name="Stacey", age="middle-aged", gender="female"),
    }

    voiced = get_voices(characters)
    assert len(voiced) == len(characters)
    assert len({voiced.voice.voice_id for voiced in voiced}) == len(voiced)
    for voiced in voiced:
        assert voiced.character in characters
        assert voiced.voice.age_group == voiced.character.age
        assert voiced.voice.gender == voiced.character.gender
