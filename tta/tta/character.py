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
