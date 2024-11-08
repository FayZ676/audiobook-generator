from tta.script import convert_text_to_script, Script, Speech
from tta.character import Character, CharacterVoiced, map_characters_to_voices
from tta.voices import voices_catalogue

def test_convert_text_to_script_success():
    """Test successful conversion of text to script, 
    ensuring that speeches are correctly mapped to characters."""
    characters = [
        Character(name="Beatrice", age="child", gender="female"),
        Character(name="Eve", age="middle-aged", gender="female"),
        Character(name="Christopher", age="child", gender="male")
    ]
    character_voiced_list = map_characters_to_voices(characters)

    # Set up sample text for conversion
    sample_text = """
    Beatrice looked at Bob with a smile. "This is a wonderful day," she said. 
    Eve nodded, replying, "Indeed, it truly is." Christopher, watching them both, laughed.
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
        Character(name="Beatrice", age="child", gender="female"),
        Character(name="Eve", age="middle-aged", gender="female"),
        Character(name="Christopher", age="child", gender="male")
    ]
    character_voiced_list = map_characters_to_voices(characters)

    # Set up text with dialogue and non-dialogue sections
    text = """
    Beatrice looked at Bob with a smile. "This is a wonderful day," she said. 
    Christopher, watching them both, laughed.
    """

    script = convert_text_to_script(text, character_voiced_list)

    # Check if narrator is included
    narrator_voice = next((voice for voice in voices_catalogue if voice.id == "narrator"), None)
    narrator_included = any(
        speech.character.voice.id == narrator_voice.id for speech in script.speeches
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
        Character(name="Beatrice", age="child", gender="female"),
        Character(name="Eve", age="middle-aged", gender="female"),
        Character(name="Christopher", age="child", gender="male")
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
