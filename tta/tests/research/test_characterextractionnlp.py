from pathlib import Path

from tta.research.characterextractionnlp import main as M
from tta.metrics import test_precision_recall


EXPECTED = {
    "Professor McGonagall",
    "Albus Dumbledore",
    "Mrs. Dursley",
    "Mr. Dursley",
    "Hagrid",
}


def main(text: str):
    result = M(text, 3)
    for r in result:
        print(r)
    precision, recall = test_precision_recall(result, EXPECTED)
    print(f"Main -> PRECISION: {precision}, RECALL: {recall}")


def get_text():
    with open(Path.cwd() / "../text/harrypotter-1.txt", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    main(get_text())
