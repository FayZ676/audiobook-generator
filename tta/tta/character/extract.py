from collections import defaultdict
import json
from concurrent.futures import ThreadPoolExecutor

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


def get_traits(chunk: str, names: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        ages_future = executor.submit(get_ages, chunk, names)
        genders_future = executor.submit(get_genders, chunk, names)
        ages = ages_future.result()
        genders = genders_future.result()
    return ages, genders


def get_pronouns(text: str, names: list[str]) -> dict[str, str]:
   # NATHAN'S ADDITIONS
    ner = NER()
    doc = ner.nlp(text)
    pronoun_map = defaultdict(lambda: "unknown")  # Default to "unknown" if no match

    # Default pronouns (can we add more?)
    male_pronouns = {"he", "him", "his"}
    female_pronouns = {"she", "her", "hers"}
    neutral_pronouns = {"they", "them", "their", "theirs"}

    # Analyze context around each name
    for name in names:
        for ent in doc.ents:
            if ent.text == name and ent.label_ == "PERSON":
                # Check surrounding tokens for pronouns
                start = max(0, ent.start - 5)
                end = min(len(doc), ent.end + 5)
                context = doc[start:end]

                # Infer pronouns based on keywords in the context
                if any(token.text.lower() in male_pronouns for token in context):
                    pronoun_map[name] = "he/him"
                elif any(token.text.lower() in female_pronouns for token in context):
                    pronoun_map[name] = "she/her"
                elif any(token.text.lower() in neutral_pronouns for token in context):
                    pronoun_map[name] = "they/them"

    return dict(pronoun_map)


def get_speaker_details(text: str):
    details: set[SpeakerDetails] = set()
    for chunk in get_chunks(text, 100000):
        names = list(get_aliases(chunk, get_speaker_names(chunk)))
        ages, genders = get_traits(chunk, [name[0] for name in names])
        details.update(
            {
                SpeakerDetails(frozenset(name), age, gender)
                for name, age, gender in zip(
                    names, list(ages.values()), list(genders.values())
                )
                if name and age and gender
            }
        )
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
