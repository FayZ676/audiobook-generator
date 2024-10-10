from tta.script import convert_text_to_script, Script, Speech


BOOK_PARAGRAPH = """
Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview. 
Holmes said, "Pray take a seat, Sir Henry. Do I understand you to say that you have had a remarkable experience?"
Sir Henry responded, "Yes, I received a strange letter this morning."
The room fell silent for a moment as Holmes pondered the situation.
"""


def test_script_conversion():
    """
    Test the conversion of text into a structured script with both narration and character dialogue.
    """
    script: Script = convert_text_to_script(BOOK_PARAGRAPH)
    expected_script = Script(
        speeches=[
            Speech(
                speaker="Narrator",
                text="Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview.",
            ),
            Speech(
                speaker="Holmes",
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
