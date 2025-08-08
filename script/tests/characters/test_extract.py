from pathlib import Path

import pytest

from tta_script.character.extract import (
    get_character_names,
    get_ages,
    get_genders,
    get_aliases,
    get_characters,
)
from tta_script.metrics import precision_recall
from tta_types.types import Character


def get_text(name: str):
    with open(Path.cwd() / f"../text/{name}", encoding="utf-8") as f:
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
    result = get_character_names(get_text("harrypotter-1-3.txt"))
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


@pytest.mark.integration
def test_get_speaker_details_with_previous_speakers():
    """Test that previous speakers are included and new ones are filtered correctly"""
    previous_characters = {
        Character(
            names=["Harry Potter"],
            age="young",
            gender="male",
        ),
        Character(
            names=["Professor McGonagall"],
            age="middle-aged",
            gender="female",
        ),
    }

    result = get_characters(
        'Harry Potter said "Hello!" Then Hermione replied "Hi there!"',
        previous_characters,
    )

    harry_found = any("Harry Potter" in speaker.names for speaker in result)
    mcgonagall_found = any(
        "Professor McGonagall" in speaker.names for speaker in result
    )

    assert harry_found, "Harry Potter should be included from previous speakers"
    assert (
        mcgonagall_found
    ), "Professor McGonagall should be included from previous speakers"
