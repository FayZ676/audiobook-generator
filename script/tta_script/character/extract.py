import json
from concurrent.futures import ThreadPoolExecutor

from tta_script.models.text import generate_text
from tta_script.ner import NER
from tta_script.text_utils import (
    remove_dialogue,
    near_quotes,
    reduce_names,
    get_chunks,
)
from tta_script.character.prompts import alias, ages, genders
from tta_script.character.types import (
    AgesResponse,
    AliasResponse,
    GendersResponse,
    SpeakerDetails,
)


def get_traits(chunk: str, names: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        ages_future = executor.submit(get_ages, chunk, names)
        genders_future = executor.submit(get_genders, chunk, names)
        ages = ages_future.result()
        genders = genders_future.result()
    return ages, genders


def get_speaker_details(text: str):
    """
    Extract speaker details from the provided text using NER to identify names and LLMs to determine their traits.
    """
    details: set[SpeakerDetails] = set()
    for chunk in get_chunks(text, 100000):
        names = list(get_aliases(chunk, get_speaker_names(chunk)))
        ages, genders = get_traits(chunk, [name[0] for name in names])
        details.update(
            {
                # TODO: We need to make sure that age and gender are typed correctly.
                SpeakerDetails(frozenset(name), age, gender)
                for name, age, gender in zip(
                    names, list(ages.values()), list(genders.values())
                )
                if name and age and gender
            }
        )
    # NOTE: We are hardcoding the narratiorn SpeakerDetails here. We do something similar in `get_dialogue_details`. Is this necessary?
    details.add(SpeakerDetails(frozenset(["Narrator"]), "middle-aged", "male"))
    return details


def get_speaker_names(text: str) -> set[str]:
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
