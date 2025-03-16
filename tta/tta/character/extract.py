import json

from tta.models.text import generate_text
from tta.ner import NER
from tta.text_utils import remove_dialogue, near_quotes, reduce_names, get_chunks
from tta.character.prompts import alias, ages, genders
from tta.character.types import (
    AgesResponse,
    AliasResponse,
    GendersResponse,
    SpeakerDetails,
)


def get_speaker_details(text: str):
    details: set[SpeakerDetails] = set()
    for chunk in get_chunks(text, 100000):
        names = list(get_aliases(chunk, get_speakers(chunk)))
        # TODO: Get ages and genders in parallel
        ages = get_ages(chunk, [name[0] for name in names])
        genders = get_genders(chunk, [name[0] for name in names])
        details.update(
            {
                # TODO: Parse age and gender
                SpeakerDetails(frozenset(name), age, gender)
                for name, age, gender in zip(
                    names, list(ages.values()), list(genders.values())
                )
                if name and age and gender
            }
        )
    return details


# TODO: Rename to get_speaker_names
def get_speakers(text: str) -> set[str]:
    paragraphs = [
        remove_dialogue(p.replace("\n", " "))
        for p in text.split("\n\n")
        if p.count('"') % 2 == 0 and p.count('"') > 0
    ]
    ner = NER()
    names = reduce_names(
        {name for paragraph in paragraphs for name in ner.find_names(paragraph)}
    )
    return {name for p in paragraphs for name in names if near_quotes(name, p)}


def get_ages(text: str, names: list[str]) -> dict[str, str]:
    result = generate_text(
        "", ages.substitute({"text": text, "characters": names}), AgesResponse
    )
    return dict(zip(names, [str(age) for age in json.loads(result)["ages"]]))


def get_genders(text: str, names: list[str]) -> dict[str, str]:
    result = generate_text(
        "", genders.substitute({"text": text, "characters": names}), GendersResponse
    )
    return dict(zip(names, [str(gender) for gender in json.loads(result)["genders"]]))


def get_aliases(text: str, names: set[str]) -> set[tuple[str]]:
    result = generate_text(
        "", alias.substitute({"text": text, "names": names}), AliasResponse
    )
    return {tuple(alias) for alias in json.loads(result)["aliases"]}
