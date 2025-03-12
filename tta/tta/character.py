import json
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
from string import Template

from pydantic import BaseModel

from tta.models.text import generate_text
from tta.ner import NER
from tta.text_utils import remove_dialogue, near_quotes, reduce_names

load_dotenv()


@dataclass(eq=True, frozen=True)
class Character:
    name: str
    age: Literal["young", "middle-aged", "old"]
    gender: Literal["male", "female"]


class ResponseFormat(BaseModel):
    response: list[Character]


class AliasResponse(BaseModel):
    aliases: list[list[str]]


class AgeResponse(BaseModel):
    ages: list[str]


def identify_characters(text: str, known_characters: set[str]) -> set[Character]:
    result = generate_text(
        "",
        prompt.substitute({"text": text, "known_characters": known_characters}),
        ResponseFormat,
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
        "", ages_prompt.substitute({"text": text, "characters": names}), AgeResponse
    )
    return [str(age) for age in json.loads(result)["ages"]]


def resolve_aliases(text: str, names: set[str]) -> set[tuple[str]]:
    result = generate_text(
        "", alias_prompt.substitute({"text": text, "names": names}), AliasResponse
    )
    return {tuple(alias) for alias in json.loads(result)["aliases"]}


prompt = Template(
    """
<text>
$text
</text>

<known_speakers>
$known_characters
<known_speakers/>

Analyze the above <text> and identify the speaking characters.
Include their age (young, middle-aged, or elder), and their gender (male, or female).
Keep the spelling of names consistent with the <known_speakers> where relevant.
"""
)


alias_prompt = Template(
    """
<text>
$text
</text>

<names>
$names
</names>

## Instructions
Analyze the above <text> and <names> and determine whether any names are aliases for one another. Aliases are different names that refer to the same character.
All names in <names> must be accounted for. Either categorize aliases together or keep individual names as distinct names.
Include any other aliases mentioned in the text that aren't included in <names>.

## Response Format
Your response must conform to the following format:
[
    ["Name 1", "Name 2"],  # Name with two aliases.
    ["Name 1", "Name 2", "Name 3"],  # Name with three aliases.
    ["Name 1"],  # Name with no aliases.
    ...
]
"""
)


ages_prompt = Template(
    """
<text>
$text
</text>

<characters>
$characters
</characters>

## Instructions
Use the above <text> to identify the age group that each character in <characters> falls into. The options are "young", "middle-aged", or "old".

## Age Group Definitions
"young" is anyone considered a child to teenager.
"middle-aged" is anyone between older than a teenager but younger than an elderly person.
"old" is anyone clearly or explicitly an elderly person.

Return the age group for the characters in the same order that they appear in <characters>.

## Response Format
Your response must conform to the following JSON format:
{
    ages: ["young", "middle-aged", "old", ...]
}
"""
)
