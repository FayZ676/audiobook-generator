from pathlib import Path

from tta.dialogue.extract import get_dialogue
from tta.character.types import SpeakerDetails


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def test_get_dialogue__hp_sample():
    speakers = {
        SpeakerDetails(frozenset({"Narrator"}), "middle-aged", "male"),
        SpeakerDetails(frozenset({"Dumbledore"}), "old", "male"),
        SpeakerDetails(frozenset({"Professor McGonagall"}), "middle-aged", "female"),
    }
    script = get_dialogue(get_text("harrypotter-sample.txt").replace("\n", " "), speakers)
    for s in script:
        print(s)
