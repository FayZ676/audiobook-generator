from pathlib import Path

from tta.character import get_speakers, resolve_aliases
from tta.metrics import precision_recall


def get_text(name: str):
    with open(Path.cwd() / f"text/{name}", encoding="utf-8") as f:
        return f.read()


def test_get_speakers__hp_chapter_1():
    expected = {
        ("Professor McGonagall",),
        ("Albus Dumbledore",),
        ("Mrs. Dursley",),
        ("Mr. Dursley",),
        ("Hagrid",),
    }
    result = get_speakers(get_text("harrypotter-1.txt"))
    precision, recall = precision_recall(result, expected)
    print(f"Main -> PRECISION: {precision}, RECALL: {recall}")
    assert result == expected


def test_get_speakers__hp_chapter_1_3():
    expected = {
        ("Professor McGonagall",),
        ("Albus Dumbledore",),
        ("Mrs. Dursley",),
        ("Mr. Dursley",),
        ("Hagrid",),
        ("Uncle Vernon",),
        ("Aunt Petunia",),
        ("Dudley",),
        ("Harry Potter",),
    }
    result = get_speakers(get_text("harrypotter-1-3.txt"))
    precision, recall = precision_recall(result, expected)
    print(f"Main -> PRECISION: {precision}, RECALL: {recall}")
    assert result == expected


def test_resolve_aliases():
    expected = {
        ("Professor McGonagall",),
        ("Albus Dumbledore",),
        ("Mrs. Dursley", "Aunt Petunia"),
        ("Mr. Dursley", "Uncle Vernon"),
        ("Hagrid",),
        ("Dudley",),
        ("Harry Potter",),
    }
    names = {
        "Professor McGonagall",
        "Albus Dumbledore",
        "Mrs. Dursley",
        "Aunt Petunia",
        "Mr. Dursley",
        "Uncle Vernon",
        "Hagrid",
        "Dudley",
        "Harry Potter",
    }
    result = resolve_aliases(get_text("harrypotter-1-3.txt"), names)
    assert result == expected
