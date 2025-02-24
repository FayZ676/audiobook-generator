from tta.research.characterextraction import nathan as N
from tta.research.characterextraction.main import main as M
from tta.metrics import test_precision_recall


EXPECTED = {
    "Professor McGonagall",
    "Dumbledore",
    "Mrs. Dursley",
    "Mr. Dursley",
    "Hagrid",
}


def nathan(text: str):
    result = N.main(text)
    precision, recall = test_precision_recall(result, EXPECTED)
    print(f"Nathan -> PRECISION: {precision}, RECALL: {recall}")


def main(text: str):
    result = M(text)
    precision, recall = test_precision_recall(result, EXPECTED)
    print(f"Main -> PRECISION: {precision}, RECALL: {recall}")


if __name__ == "__main__":
    # CHANGE PATHING FOR TXT FILE
    with open(
        "c:/Users/Nathan/audiobook-generator-1/tta/tests/text/harrypotter-1.txt",
        encoding="utf-8",
    ) as f:
        text = f.read()

    nathan(text)
    main(text)
