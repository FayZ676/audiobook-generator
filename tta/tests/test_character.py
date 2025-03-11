from pathlib import Path

from tta.character import get_speakers
from tta.metrics import precision_recall


def get_text():
    with open(Path.cwd() / "text/harrypotter-1.txt", encoding="utf-8") as f:
        return f.read()


def test_get_speakers():
    expected = {
        ("Professor McGonagall",),
        ("Albus Dumbledore",),
        ("Mrs. Dursley",),
        ("Mr. Dursley",),
        ("Hagrid",),
    }
    result = get_speakers(get_text())
    precision, recall = precision_recall(result, expected)
    print(f"Main -> PRECISION: {precision}, RECALL: {recall}")
    assert result == expected
