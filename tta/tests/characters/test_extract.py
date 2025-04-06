from pathlib import Path

import pytest

from tta.character.extract import (
    get_speaker_names,
    get_ages,
    get_genders,
    get_aliases,
    get_speaker_details,
    get_traits
)
from tta.metrics import precision_recall


def get_text(name: str):
    with open(Path.cwd() / f"text/{name}", encoding="utf-8") as f:
        return f.read()

def test_get_speakers__hp_chapter_1_3():
    expected = {
        "Professor McGonagall",
        "Albus Dumbledore",
        "Mrs. Dursley",
        "Mr. Dursley",
        "Hagrid",
        "Uncle Vernon",
        "Aunt Petunia",
        "Dudley",
        "Harry Potter",
    }
    result = get_speaker_names(get_text("harrypotter-1-3.txt"))
    precision, recall = precision_recall(result, expected)
    print(f"Main -> PRECISION: {precision}, RECALL: {recall}")
    assert result == expected

def test_precision_recall_computed_empty():
    expected = {"Harry Potter", "Hagrid"}
    result = set() 
    precision, recall = precision_recall(result, expected)
    print(f"PRECISION: {precision}, RECALL: {recall}")
    assert precision == 0.0
    assert recall == 0.0

def test_precision_recall_expected_empty():
    expected = set()
    result = {"Harry Potter", "Hagrid"}
    precision, recall = precision_recall(result, expected)
    print(f"PRECISION: {precision}, RECALL: {recall}")
    assert precision == 0.0
    assert recall == 0.0

def test_precision_recall_partial_match():
    expected = {"Harry Potter", "Hagrid", "Dumbledore"}
    result = {"Harry Potter", "Hagrid", "Snape"} 
    precision, recall = precision_recall(result, expected)
    print(f"PRECISION: {precision}, RECALL: {recall}")
    assert round(precision, 2) == 0.67
    assert round(recall, 2) == 0.67

@pytest.mark.integration
def test_resolve_aliases():
    expected = {
        tuple(sorted(group)) for group in {
            ('Dudley',), 
            ('Professor McGonagall',), 
            ('Albus Dumbledore',), 
            ('Uncle Vernon', 'Mr. Dursley'), 
            ('Harry Potter',), 
            ('Hagrid',), 
            ('Mrs. Dursley', 'Aunt Petunia'), 
        }
    }
    names = {
        "Professor McGonagall",
        "Albus Dumbledore",
        "Aunt Petunia",
        "Mrs. Dursley",
        "Mr. Dursley",
        "Uncle Vernon",
        "Hagrid",
        "Dudley",
        "Harry Potter",
    }
    result = {
        tuple(sorted(group)) for group in get_aliases(get_text("harrypotter-1-3.txt"), names)
    }
    assert result == expected


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
    assert (
        get_ages(get_text("harrypotter-1-3.txt"), [name for name in names_ages])
        == names_ages
    )


@pytest.mark.integration
def test_get_genders__hp_chapter_1_3():
    names_genders = {
        "Professor McGonagall": "female",
        "Albus Dumbledore": "male",
        "Mrs. Dursley": "female",
        "Mr. Dursley": "male",
        "Hagrid": "male",
        "Uncle Vernon": "male",
        "Aunt Petunia": "female",
        "Dudley": "male",
        "Harry Potter": "male",
    }
    assert (
        get_genders(get_text("harrypotter-1-3.txt"), [name for name in names_genders])
        == names_genders
    )


# def test_get_speaker_details():
#     for detail in get_speaker_details(get_text("harrypotter-1-3.txt")):
#         print(detail)

def test_get_speaker_details__hp_chapter_1_3():
    result = get_speaker_details(get_text("harrypotter-1-3.txt"))
    expected_names = {
        frozenset(["Professor McGonagall"]),
        frozenset(["Albus Dumbledore"]),
        frozenset(["Mrs. Dursley", "Aunt Petunia"]),
        frozenset(["Mr. Dursley", "Uncle Vernon"]),
        frozenset(["Hagrid"]),
        frozenset(["Dudley"]),
        frozenset(["Harry Potter"]),
        frozenset(["Narrator"]),
    }
    result_names = {r.names for r in result}
    assert result_names == expected_names

def test_get_traits__basic_check():
    text = get_text("harrypotter-1-3.txt")
    names = ["Harry Potter", "Hagrid"]
    ages, genders = get_traits(text, names)
    assert all(name in ages for name in names)
    assert all(name in genders for name in names)
