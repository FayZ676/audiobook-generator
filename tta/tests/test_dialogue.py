from pathlib import Path

from tta.dialogue import get_dialogue


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def test_get_dialogue__hp_sample():
    names = {"Dumbledore", "Professor Mcgonagall"}
    script = get_dialogue(
        get_text("harrypotter-sample.txt").replace("\n", " "), names
    )
    for s in script:
        print(s)
