import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

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
)
from tta_types.types import SpeakerDetails


@dataclass(frozen=True)
class CharacterAliases:
    names: frozenset[str]

    def primary_name(self) -> str:
        return next(iter(self.names))


def get_traits(chunk: str, names: list[str]) -> tuple[dict[str, str], dict[str, str]]:
    with ThreadPoolExecutor(max_workers=2) as executor:
        ages_future = executor.submit(get_ages, chunk, names)
        genders_future = executor.submit(get_genders, chunk, names)
        ages = ages_future.result()
        genders = genders_future.result()
    return ages, genders


def get_speaker_details(
    text: str, previous_speakers: list[SpeakerDetails]
) -> set[SpeakerDetails]:
    """
    Extract speaker details from the provided text using NER to identify names and LLMs to determine their traits.

    Args:
        text: The text to extract speakers from
        previous_speakers: List of previously found speakers (from types.SpeakerDetails) to convert and include
    """
    existing_speakers = _convert_previous_speakers(previous_speakers)
    new_speakers = _extract_new_speakers_from_text(text, existing_speakers)
    all_speakers = existing_speakers | new_speakers
    all_speakers.add(_create_narrator())
    return all_speakers


def _convert_previous_speakers(
    previous_speakers: list[SpeakerDetails],
) -> set[SpeakerDetails]:
    """Convert API format speakers to internal format."""
    return set(previous_speakers)  # No conversion needed anymore!


def _extract_new_speakers_from_text(
    text: str, existing_speakers: set[SpeakerDetails]
) -> set[SpeakerDetails]:
    """Extract new speakers from text that don't overlap with existing ones."""
    new_speakers = set()

    for chunk in get_chunks(text, 100000):
        chunk_speakers = _process_text_chunk(chunk, existing_speakers | new_speakers)
        new_speakers.update(chunk_speakers)

    return new_speakers


def _process_text_chunk(
    chunk: str, existing_speakers: set[SpeakerDetails]
) -> set[SpeakerDetails]:
    """Process a single text chunk to find new speakers."""
    character_aliases = get_aliases(chunk, get_speaker_names(chunk))
    new_aliases = _filter_overlapping_aliases(character_aliases, existing_speakers)

    if not new_aliases:
        return set()

    return _create_characters_with_traits(chunk, new_aliases)


def _filter_overlapping_aliases(
    character_aliases: set[CharacterAliases], existing_speakers: set[SpeakerDetails]
) -> list[CharacterAliases]:
    """Filter out aliases that overlap with existing speakers."""
    non_overlapping = []
    for aliases in character_aliases:
        has_overlap = any(
            any(name in existing_speaker.names for name in aliases.names)
            for existing_speaker in existing_speakers
        )
        if not has_overlap:
            non_overlapping.append(aliases)
    return non_overlapping


def _create_characters_with_traits(
    chunk: str, aliases_list: list[CharacterAliases]
) -> set[SpeakerDetails]:
    """Create SpeakerDetails with LLM-determined traits."""
    ages, genders = get_traits(
        chunk, [aliases.primary_name() for aliases in aliases_list]
    )

    return {
        SpeakerDetails(
            names=list(aliases.names),
            age=age,
            gender=gender,
        )
        for aliases, age, gender in zip(
            aliases_list,
            list(ages.values()),
            list(genders.values()),
        )
        if aliases and age and gender
    }


def _create_narrator() -> SpeakerDetails:
    """Create the standard narrator character."""
    return SpeakerDetails(
        names=["Narrator"],
        age="middle-aged",
        gender="male",
    )


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


def get_aliases(text: str, names: set[str]) -> set[CharacterAliases]:
    result = generate_text(
        "", alias.substitute({"text": text, "names": names}), AliasResponse
    )
    return {
        CharacterAliases(frozenset(alias_group))
        for alias_group in json.loads(result)["aliases"]
    }
