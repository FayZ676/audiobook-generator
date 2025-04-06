from pathlib import Path

from tta.dialogue.extract import get_dialogue_details
from tta.character.types import SpeakerDetails
from tta.voices import SpeakerVoice, Voice


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def test_get_dialogue_nlp__hp_sample():
    speakers = {
        SpeakerDetails(frozenset({"Professor McGonagall"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Albus Dumbledore"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Mrs. Dursley", "Aunt Petunia"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Mr. Dursley", "Uncle Vernon"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Hagrid"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Dudley"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Harry Potter"}), "middle-aged", "male"),
    }

    speakers_voices = {
        SpeakerVoice(
            character=s,
            voice=Voice(
                name="Dummy",
                gender=s.gender,
                age=s.age,
                voice_id="dummy_voice_id"
            )
        )
        for s in speakers
    }

    text = get_text("harrypotter-1-3.txt")
    result = get_dialogue_details(text, speakers_voices)

    with open("output.txt", "wt") as f:
        for r in result:
            f.write(f"{r}\n")


if __name__ == "__main__":
    test_get_dialogue_nlp__hp_sample()
