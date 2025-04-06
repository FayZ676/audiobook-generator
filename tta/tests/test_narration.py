import sys
from pathlib import Path
from tta.narration import get_narration_from_text


def get_text(filename: str) -> str:
    base = Path(__file__).parent / "text"
    with open(base / filename, "r", encoding="utf-8") as f:
        return f.read()


def test_narration_generation_from_text():
    text = get_text("harrypotter-sample.txt")
    print(text)
    audio_bytes = get_narration_from_text(text)

    assert isinstance(audio_bytes, bytes)
    assert len(audio_bytes) > 1000  # Arbitrary non-zero size

    output_path = Path(__file__).parent / "output_test.mp3"
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
