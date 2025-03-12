import json

from tta.models.text import generate_text
from tta.ner import NER
from tta.text_utils import remove_dialogue, near_quotes, reduce_names
from tta.character.prompts import speakers, alias, ages
from tta.character.types import SpeakersResponse, AgesResponse, AliasResponse, Character


def get_speakers_llm(text: str, known_characters: set[str]) -> set[Character]:
    result = generate_text(
        "",
        speakers.substitute({"text": text, "known_characters": known_characters}),
        SpeakersResponse,
    )
    characters = {
        Character(name=char["name"], age=char["age"], gender=char["gender"])
        for char in json.loads(result)["response"]
    }
    characters.add(Character(name="Narrator", age="middle-aged", gender="male"))
    return characters


def get_speakers(text: str) -> set[tuple[str]]:
    paragraphs = [
        remove_dialogue(p.replace("\n", " "))
        for p in text.split("\n\n")
        if p.count('"') % 2 == 0 and p.count('"') > 0
    ]
    ner = NER()
    names = reduce_names(
        {name for paragraph in paragraphs for name in ner.find_names(paragraph)}
    )
    return {(name,) for p in paragraphs for name in names if near_quotes(name, p)}


def get_ages(text: str, names: list[str]):
    result = generate_text(
        "", ages.substitute({"text": text, "characters": names}), AgesResponse
    )
    return [str(age) for age in json.loads(result)["ages"]]


def get_aliases(text: str, names: set[str]) -> set[tuple[str]]:
    result = generate_text(
        "", alias.substitute({"text": text, "names": names}), AliasResponse
    )
    return {tuple(alias) for alias in json.loads(result)["aliases"]}
