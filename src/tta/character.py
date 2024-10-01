import json
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
from string import Template

from tta.models.text_to_speech import generate_text


load_dotenv()


@dataclass
class Character:
    name: str
    age: Literal["child", "young adult", "middle-aged", "elderly"]
    gender: Literal["male", "female"]


class ResponseFormat:
    response: list[Character]


def identify_characters(text: str) -> list[Character]:
    result = generate_text(prompt.substitute({"text": text}))
    try:
        characters = json.loads(result)
        return [Character(**char) for char in characters]
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
        return []


prompt = Template(
    """
$text

Analyze the following paragraph and identify the speaking characters, their age (young, middle-aged, or elder), and gender (male, or female):

"""
)
