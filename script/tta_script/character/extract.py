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


def get_speaker_details(text: str, previous_speakers: list = None):
    """
    Extract speaker details from the provided text using NER to identify names and LLMs to determine their traits.
    
    Args:
        text: The text to extract speakers from
        previous_speakers: List of previously found speakers (from types.script.SpeakerDetails) to avoid re-finding
    """
    if previous_speakers is None:
        previous_speakers = []
    
    # Convert previous speakers to script format for comparison
    previous_speaker_names = set()
    for prev_speaker in previous_speakers:
        if hasattr(prev_speaker, 'names'):
            previous_speaker_names.update(prev_speaker.names)
    
    details: set[SpeakerDetails] = set()
    for chunk in get_chunks(text, 100000):
        names = list(get_aliases(chunk, get_speaker_names(chunk)))
        
        # Filter out names that are already in previous speakers
        filtered_names = []
        for name_tuple in names:
            # Check if any name in this tuple overlaps with previous speakers
            if not any(name in previous_speaker_names for name in name_tuple):
                filtered_names.append(name_tuple)
        
        if filtered_names:
            ages, genders = get_traits(chunk, [name[0] for name in filtered_names])
            details.update(
                {
                    # TODO: We need to make sure that age and gender are typed correctly.
                    SpeakerDetails(frozenset(name), age, gender)
                    for name, age, gender in zip(
                        filtered_names, list(ages.values()), list(genders.values())
                    )
                    if name and age and gender
                }
            )
    
    # Add previous speakers back to the result set (converted to script format)
    for prev_speaker in previous_speakers:
        if hasattr(prev_speaker, 'names'):
            script_speaker = SpeakerDetails(
                frozenset(prev_speaker.names),
                prev_speaker.age,
                prev_speaker.gender
            )
            details.add(script_speaker)
    
    # NOTE: We are hardcoding the narrator SpeakerDetails here. We do something similar in `get_script`. Is this necessary?
    details.add(SpeakerDetails(frozenset(["Narrator"]), "middle-aged", "male"))
    return details


def get_speaker_names(text: str) -> set[str]:
    paragraphs = []
    for p in text.split("\n\n"):
        if p.count('"') % 2 == 0 and p.count('"') > 0:
            paragraphs.append(remove_dialogue(p.replace("\n", " ")))
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
