import json

import pytest

from tta_script.character import extract
from tta_script.character.extract import NARRATOR, get_characters
from tta_types.types import Character


def fake_model(monkeypatch, *replies: list[dict]):
    """Make the model return each reply in turn; record the prompts it got."""
    prompts: list[str] = []
    replies_iter = iter(replies)

    def generate_text(_system, prompt, _response_format):
        prompts.append(prompt)
        return json.dumps({"characters": next(replies_iter)})

    monkeypatch.setattr(extract, "generate_text", generate_text)
    return prompts


VERNON = {"names": ["Mr. Dursley", "Uncle Vernon"], "age": "middle-aged", "gender": "male"}
PETUNIA = {"names": ["Mrs. Dursley"], "age": "middle-aged", "gender": "female"}


def test_first_chapter_adds_narrator(monkeypatch):
    fake_model(monkeypatch, [VERNON, PETUNIA])

    result = get_characters("text", set())

    assert result == {
        Character(names=["Mr. Dursley", "Uncle Vernon"], age="middle-aged", gender="male"),
        Character(names=["Mrs. Dursley"], age="middle-aged", gender="female"),
        NARRATOR,
    }


def test_later_chapter_skips_known_characters_and_narrator(monkeypatch):
    known = {
        Character(names=["Mr. Dursley"], age="middle-aged", gender="male"),
        NARRATOR,
    }
    harry = {"names": ["Harry Potter", "Harry"], "age": "young", "gender": "male"}
    prompts = fake_model(monkeypatch, [VERNON, harry])

    result = get_characters("text", known)

    # Vernon shares "Mr. Dursley" with a known character, so he isn't new.
    assert result == {Character(names=["Harry Potter", "Harry"], age="young", gender="male")}
    assert "- Mr. Dursley" in prompts[0]


def test_model_listing_a_narrator_is_ignored(monkeypatch):
    fake_model(monkeypatch, [{"names": ["Narrator"], "age": "old", "gender": "female"}])

    assert get_characters("text", set()) == {NARRATOR}


def test_blank_and_repeated_names_are_cleaned(monkeypatch):
    fake_model(
        monkeypatch,
        [{"names": [" Hagrid ", "Hagrid", "", "Rubeus Hagrid"], "age": "middle-aged", "gender": "male"}],
    )

    result = get_characters("text", {NARRATOR})

    assert result == {Character(names=["Hagrid", "Rubeus Hagrid"], age="middle-aged", gender="male")}


def test_long_text_is_split_and_later_chunks_see_earlier_finds(monkeypatch):
    monkeypatch.setattr(extract, "CHUNK_WORDS", 3)
    prompts = fake_model(monkeypatch, [VERNON], [VERNON, PETUNIA])

    result = get_characters("one two three\n\nfour five six", {NARRATOR})

    assert len(prompts) == 2
    assert "- Mr. Dursley, Uncle Vernon" in prompts[1]
    assert {c.first_alias() for c in result} == {"Mr. Dursley", "Mrs. Dursley"}


def test_invalid_reply_raises(monkeypatch):
    fake_model(monkeypatch, [{"names": ["Hagrid"], "age": "ancient", "gender": "male"}])

    with pytest.raises(ValueError):
        get_characters("text", set())
