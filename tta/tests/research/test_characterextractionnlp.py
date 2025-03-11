from pathlib import Path

from tta.research.characterextractionnlp import main as M
from tta.metrics import test_precision_recall


EXPECTATION = {
    ("Professor McGonagall",),
    ("Albus Dumbledore",),
    ("Mrs. Dursley",),
    ("Mr. Dursley",),
    ("Hagrid",),
}


def main(text: str):
    result = M(text)
    precision, recall = test_precision_recall(result, EXPECTATION)
    print(f"Main -> PRECISION: {precision}, RECALL: {recall}")
    for r in result:
        print(r)


if __name__ == "__main__":

    def get_text():
        with open(Path.cwd() / "../text/harrypotter-1.txt", encoding="utf-8") as f:
            return f.read()

    main(get_text())
