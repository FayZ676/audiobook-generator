from tta.script import convert_text_to_script, select_narrator_voice, Script, Speech
from tta.character import Character, CharacterVoiced, map_characters_to_voices
from tta.voices import VoiceCatalogue

# Initialize VoiceCatalogue for access to narrator voice
voice_catalogue = VoiceCatalogue()
all_voices = voice_catalogue.get_all_voices()
narrator_voice = select_narrator_voice(all_voices)

def test_convert_text_to_script_success():
    """Test successful conversion of text to script, 
    ensuring that speeches are correctly mapped to characters."""
    characters = [
        Character(name="Aria", age="middle-aged", gender="female"),
        Character(name="Roger", age="middle-aged", gender="male"),
        Character(name="Liam", age="young", gender="male")
    ]
    character_voiced_list = map_characters_to_voices(characters)

    # Set up sample text for conversion
    sample_text = """
    Aria looked at Roger with a smile. "This is a wonderful day," she said. 
    Roger nodded, replying, "Indeed, it truly is." Liam, watching them both, laughed.
    """

    # Test successful conversion of text to script
    script = convert_text_to_script(sample_text, character_voiced_list)
    assert isinstance(script, Script), "Result should be of type Script"
    assert len(script.speeches) > 0, "Script should contain speeches"

    # Verify that each speech is correctly mapped to a character
    for speech in script.speeches:
        assert isinstance(speech, Speech), "Each item in speeches should be of type Speech"
        assert isinstance(speech.character, CharacterVoiced), "Character in speech should be CharacterVoiced"
        assert speech.text, "Speech should contain text"

def test_narrator_inclusion():
    """Test that the narrator is included for non-dialogue text."""
    # Set up character data directly in the test
    characters = [
        Character(name="Aria", age="middle-aged", gender="female"),
        Character(name="Roger", age="middle-aged", gender="male"),
        Character(name="Liam", age="young", gender="male")
    ]
    character_voiced_list = map_characters_to_voices(characters)

    # Ensure narrator_voice is available
    assert narrator_voice is not None, "Narrator voice should be selected based on traits."

    # Set up text with dialogue and non-dialogue sections
    text = """
    Aria looked at Roger with a smile. "This is a wonderful day," she said.
    Liam, watching them both, laughed.
    """

    script = convert_text_to_script(text, character_voiced_list)

    # Check if narrator is included in non-dialogue portions of the script
    narrator_included = any(
        speech.character.voice.voice_id == narrator_voice.voice_id for speech in script.speeches
    )
    assert narrator_included, "Narrator should be included in the script for non-dialogue text"


def test_empty_response():
    """Test the handling of an empty input text, ensuring that no speeches are included."""
    # Set up an empty input scenario
    empty_script = convert_text_to_script("", [])

    # Ensure script is generated even if text is empty
    assert empty_script is not None, "Script should be generated even if text is empty"
    assert len(empty_script.speeches) == 0, "Script should contain no speeches for empty text"


def test_invalid_response_handling():
    """Test the handling of an invalid response format, 
    ensuring a narrator speech is included if necessary."""
    # Set up text with invalid format
    invalid_text = """
    NARRATOR: This is invalid format, missing text.
    """
    characters = [
        Character(name="Aria", age="middle-aged", gender="female"),
        Character(name="Roger", age="middle-aged", gender="male"),
        Character(name="Liam", age="young", gender="male")
    ]
    character_voiced_list = map_characters_to_voices(characters)

    # Convert invalid text
    script = convert_text_to_script(invalid_text, character_voiced_list)
    assert script is not None, "Script should be generated despite invalid format"

    # Expect at least one valid narrator assignment in case of unstructured text
    narrator_speeches = [
        s for s in script.speeches if s.character.character.name == "Narrator"
    ]
    assert len(narrator_speeches) >= 1, "Script should contain at least one narrator speech for unassigned lines"
