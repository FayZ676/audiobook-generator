import json
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
from string import Template

from pydantic import BaseModel

from tta.models.text import generate_text

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
