from tta.script import convert_text_to_script, Script, Speech
from tta.character import Character


BOOK_PARAGRAPH = """
Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview. 
Holmes said, "Pray take a seat, Sir Henry. Do I understand you to say that you have had a remarkable experience?"
Sir Henry responded, "Yes, I received a strange letter this morning."
The room fell silent for a moment as Holmes pondered the situation.
"""

CHARACTERS = [
    Character(name="Sherlock Holmes", age="middle-aged", gender="male"),
    Character(name="Sir Henry", age="middle-aged", gender="male"),
]


def test_script_conversion():
    """
    Test the conversion of text into a structured script with both narration and character dialogue.
    """
    script: Script = convert_text_to_script(BOOK_PARAGRAPH, CHARACTERS)
    print(script)
    expected_script = Script(
        speeches=[
            Speech(
                speaker="Narrator",
                text="Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview.",
            ),
            Speech(
                speaker="Sherlock Holmes",
                text="Pray take a seat, Sir Henry. Do I understand you to say that you have had a remarkable experience?",
            ),
            Speech(
                speaker="Sir Henry",
                text="Yes, I received a strange letter this morning.",
            ),
            Speech(
                speaker="Narrator",
                text="The room fell silent for a moment as Holmes pondered the situation.",
            ),
        ]
    )
    assert script == expected_script, f"Expected {expected_script}, but got {script}"
