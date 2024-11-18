from tta.script import convert_text_to_script, Speech
from tta.character import CharacterVoiced, Character, Voice


BOOK_PARAGRAPH = """
Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview. 
Holmes said, "Pray take a seat, Sir Henry. Do I understand you to say that you have had a remarkable experience?"
Sir Henry responded, "Yes, I received a strange letter this morning."
The room fell silent for a moment as Holmes pondered the situation.
"""

CHARACTERS = [
    CharacterVoiced(
        character=Character(name="Sherlock Holmes", age="middle-aged", gender="male"),
        voice=Voice(
            voice_id="123",
            name="Sherlock Holmes",
            gender="male",
            age_group="middle-aged",
        ),
    ),
    CharacterVoiced(
        character=Character(name="Sir Henry", age="middle-aged", gender="male"),
        voice=Voice(
            voice_id="456",
            name="Sir Henry",
            gender="male",
            age_group="middle-aged",
        ),
    ),
]


# TODO: Need to fix this test. Not reliable.
def test_script_conversion():
    """
    Test the conversion of text into a structured script with both narration and character dialogue.
    """
    script: list[Speech] | None = convert_text_to_script(BOOK_PARAGRAPH, CHARACTERS)
    print(script)
    expected_script = [
        Speech(
            speaker="Narrator",
            voice_id="",
            text="Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview.",
        ),
        Speech(
            speaker="Sherlock Holmes",
            voice_id="123",
            text="Pray take a seat, Sir Henry. Do I understand you to say that you have had a remarkable experience?",
        ),
        Speech(
            speaker="Sir Henry",
            voice_id="456",
            text="Yes, I received a strange letter this morning.",
        ),
        Speech(
            speaker="Narrator",
            voice_id="",
            text="The room fell silent for a moment as Holmes pondered the situation.",
        ),
    ]
    assert script == expected_script, f"Expected {expected_script}, but got {script}"
