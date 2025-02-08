from tta.research.characterextraction import derrick as D
from tta.research.characterextraction import nathan as N
from tta.metrics import test_precision_recall


EXPECTED = {
    "Professor McGonagall",
    "Dumbledore",
    "Mrs. Dursley",
    "Mr. Dursley",
}


def test_nathan(text: str):
    result = N.main(text)
    precision, recall = test_precision_recall(result, EXPECTED)
    print(f"Nathan -> PRECISION: {precision}, RECALL: {recall}")


def test_derrick(text: str):
    result = D.main(text)
    precision, recall = test_precision_recall(result, EXPECTED)
    print(f"Derrick -> PRECISION: {precision}, RECALL: {recall}")


if __name__ == "__main__":
    with open("../text/harrypotter-1-3.txt", encoding="utf-8") as f:
        text = f.read()

    test_nathan(text)
    test_derrick(text)
