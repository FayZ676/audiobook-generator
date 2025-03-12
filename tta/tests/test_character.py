from pathlib import Path

import pytest

from tta.character.extract import get_speakers, get_ages, get_aliases
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


@pytest.mark.integration
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
    result = get_aliases(get_text("harrypotter-1-3.txt"), names)
    assert result == expected


@pytest.mark.integration
def test_get_age__hp_chapter_1():
    names_ages = {
        "Professor McGonagall": "middle-aged",
        "Albus Dumbledore": "old",
        "Mrs. Dursley": "middle-aged",
        "Mr. Dursley": "middle-aged",
        "Hagrid": "middle-aged",
    }
    assert get_ages(
        get_text("harrypotter-1.txt"), [name for name in names_ages]
    ) == list(names_ages.values())


@pytest.mark.integration
def test_get_age__hp_chapter_1_3():
    names_ages = {
        "Professor McGonagall": "middle-aged",
        "Albus Dumbledore": "old",
        "Mrs. Dursley": "middle-aged",
        "Mr. Dursley": "middle-aged",
        "Hagrid": "middle-aged",
        "Uncle Vernon": "middle-aged",
        "Aunt Petunia": "middle-aged",
        "Dudley": "young",
        "Harry Potter": "young",
    }
    assert get_ages(
        get_text("harrypotter-1-3.txt"), [name for name in names_ages]
    ) == list(names_ages.values())
