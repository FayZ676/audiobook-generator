from pathlib import Path

from tta.dialogue.extract import get_dialogue_details, create_dialogue_batches
from tta.dialogue.types import TextSegment
from tta.character.types import SpeakerDetails
from tta.voices import SpeakerVoice, Voice


def get_text(filename: str) -> str:
    current_dir = Path(__file__).parent
    with open(f"{current_dir}/text/{filename}", "r", encoding="utf-8") as f:
        return f.read()


def test_create_dialogue_batches():
    dialogues = [
        TextSegment("Hello, how are you?", True),
        TextSegment("asked Bob.", False),
        TextSegment("Great! How about you?", True),
        TextSegment("replied Mary.", False),
    ]
    expected_batches = [
        {
            0: TextSegment("Hello, how are you?", True),
            1: TextSegment("asked Bob.", False),
        },
        {
            2: TextSegment("Great! How about you?", True),
            3: TextSegment("replied Mary.", False),
        },
    ]
    assert create_dialogue_batches(dialogues, 2) == expected_batches


if __name__ == "__main__":

    def test_get_dialogue_nlp__hp_sample():
        speakers = {
            SpeakerVoice(
                SpeakerDetails(
                    frozenset({"Professor McGonagall"}), "middle-aged", "male"
                ),
                Voice("name", "male", "young", "abc123"),
            ),
            SpeakerVoice(
                SpeakerDetails(frozenset({"Albus Dumbledore"}), "middle-aged", "male"),
                Voice("name", "male", "young", "abc123"),
            ),
            SpeakerVoice(
                SpeakerDetails(
                    frozenset({"Mrs. Dursley", "Aunt Petunia"}), "middle-aged", "male"
                ),
                Voice("name", "male", "young", "abc123"),
            ),
            SpeakerVoice(
                SpeakerDetails(
                    frozenset({"Mr. Dursley", "Uncle Vernon"}), "middle-aged", "male"
                ),
                Voice("name", "male", "young", "abc123"),
            ),
            SpeakerVoice(
                SpeakerDetails(frozenset({"Hagrid"}), "middle-aged", "male"),
                Voice("name", "male", "young", "abc123"),
            ),
            SpeakerVoice(
                SpeakerDetails(frozenset({"Dudley"}), "middle-aged", "male"),
                Voice("name", "male", "young", "abc123"),
            ),
            SpeakerVoice(
                SpeakerDetails(frozenset({"Harry Potter"}), "middle-aged", "male"),
                Voice("name", "male", "young", "abc123"),
            ),
        }
        result = get_dialogue_details(get_text("harrypotter-1-3.txt"), speakers)
        with open("output.txt", "wt") as f:
            for r in result:
                f.write(f"{r}\n")

    test_get_dialogue_nlp__hp_sample()
