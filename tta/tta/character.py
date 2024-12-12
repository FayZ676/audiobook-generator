import json
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv
from string import Template

from pydantic import BaseModel

from tta.models.text import generate_text
from tta.voices import Voice, VoiceCatalogue

load_dotenv()


@dataclass(eq=True, frozen=True)
class Character:
    name: str
    age: Literal["young", "middle-aged", "old"]
    gender: Literal["male", "female"]


@dataclass(eq=True, frozen=True)
class CharacterVoiced:
    character: Character
    voice: Voice


class ResponseFormat(BaseModel):
    response: list[Character]


def identify_characters(text: str, known_characters: set[str]) -> set[CharacterVoiced]:
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
    return _map_characters_to_voices(characters)


### private ###


def _map_characters_to_voices(characters: set[Character]) -> set[CharacterVoiced]:
    available_voices = VoiceCatalogue().get_all_voices()
    voiced_characters = set()
    for character in characters:
        matching_voices = [
            voice
            for voice in available_voices
            if voice.age_group == character.age and voice.gender == character.gender
        ]

        if matching_voices:
            selected_voice = matching_voices[0]
            available_voices.remove(selected_voice)
            voiced_characters.add(
                CharacterVoiced(character=character, voice=selected_voice)
            )
        else:
            raise ValueError(
                f"No available voices for {character.name} with age {character.age} and gender {character.gender}"
            )
    return voiced_characters


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
