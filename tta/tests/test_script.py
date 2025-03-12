from pathlib import Path
from tta.script import convert_text_to_script, Speech
from tta.character.types import Character
from tta.voices import CharacterVoiced, Voice


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}.txt", "r", encoding="utf-8") as f:
        return f.read()


def test_convert_text_to_script__sherlock():
    SHERLOCK_CHARACTERS = {
        CharacterVoiced(
            character=Character(
                name="Sherlock Holmes", age="middle-aged", gender="male"
            ),
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
        CharacterVoiced(
            character=Character(name="Narrator", age="middle-aged", gender="male"),
            voice=Voice(
                voice_id="789",
                name="Narrator",
                gender="male",
                age_group="middle-aged",
            ),
        ),
    }
    script: list[Speech] | None = convert_text_to_script(
        get_text("sherlock").replace("\n", " "), SHERLOCK_CHARACTERS
    )
    expected_script = [
        Speech(
            speaker="Narrator",
            voice_id="789",
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
            voice_id="789",
            text="The room fell silent for a moment as Holmes pondered the situation.",
        ),
    ]
    assert script == expected_script, f"Expected {expected_script}, but got {script}"


def test_convert_text_to_script__harry_potter():
    HARRY_POTTER_CHARACTERS = {
        CharacterVoiced(
            character=Character(name="Dumbledore", age="old", gender="male"),
            voice=Voice(
                voice_id="123",
                name="Dumbledore",
                gender="male",
                age_group="old",
            ),
        ),
        CharacterVoiced(
            character=Character(
                name="Professor McGonagall", age="middle-aged", gender="female"
            ),
            voice=Voice(
                voice_id="456",
                name="Professor McGonagall",
                gender="female",
                age_group="middle-aged",
            ),
        ),
        CharacterVoiced(
            character=Character(name="Narrator", age="middle-aged", gender="male"),
            voice=Voice(
                voice_id="789",
                name="Narrator",
                gender="male",
                age_group="middle-aged",
            ),
        ),
    }
    script: list[Speech] | None = convert_text_to_script(
        get_text("harrypotter").replace("\n", " "), HARRY_POTTER_CHARACTERS
    )
    expected_script = [
        Speech(
            speaker="Professor McGonagall",
            voice_id="456",
            text="You'd be stiff if you'd been sitting on a brick wall all day.",
        ),
        Speech(
            speaker="Dumbledore",
            voice_id="123",
            text="All day? When you could have been celebrating? I must have passed a dozen feasts and parties on my way here.",
        ),
        Speech(
            speaker="Narrator",
            voice_id="789",
            text="Professor McGonagall sniffed angrily.",
        ),
        Speech(
            speaker="Professor McGonagall",
            voice_id="456",
            text="Oh yes, everyone's celebrating, all right. You'd think they'd be a bit more careful, but no -- even the Muggles have noticed something's going on. It was on their news.",
        ),
        Speech(
            speaker="Narrator",
            voice_id="789",
            text="She jerked her head back at the Dursleys' dark living-room window.",
        ),
        Speech(
            speaker="Professor McGonagall",
            voice_id="456",
            text="I heard it. Flocks of owls... shooting stars... Well, they're not completely stupid. They were bound to notice something. Shooting stars down in Kent -- I'll bet that was Dedalus Diggle. He never had much sense.",
        ),
    ]
    assert script == expected_script, f"Expected {expected_script}, but got {script}"
