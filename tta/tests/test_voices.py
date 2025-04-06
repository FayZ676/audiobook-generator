from tta.character.types import SpeakerDetails
from tta.voices import get_voices


def test_map_characters_to_voices():
    """Test the mapping of characters to voices ensuring all voices are unique"""

    characters = {
        SpeakerDetails(frozenset({"Gwen"}), "young", "female"),
        SpeakerDetails(frozenset({"Adam"}), "young", "male"),    
    }

    voiced = get_voices(characters)
    assert len(voiced) == len(characters)
    assert len({voiced.voice.voice_id for voiced in voiced}) == len(voiced)
    for voiced in voiced:
        assert voiced.character in characters
        assert voiced.voice.age == voiced.character.age
        assert voiced.voice.gender == voiced.character.gender
