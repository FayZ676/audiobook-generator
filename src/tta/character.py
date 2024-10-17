import json
from dataclasses import dataclass
from typing import Literal, List
from dotenv import load_dotenv
from string import Template

from pydantic import BaseModel

from tta.models.text import generate_text
from tta.voices import Voice, voices_catalogue  

load_dotenv()

@dataclass
class Character:
    name: str
    age: Literal["child", "young adult", "middle-aged", "elderly"]
    gender: Literal["male", "female"]

@dataclass
class CharacterVoiced:
    character: Character
    voice: Voice

class ResponseFormat(BaseModel):
    response: list[Character]

def identify_characters(text: str) -> list[Character]:
    result = generate_text(prompt.substitute({"text": text}), ResponseFormat)
    try:
        characters = json.loads(result)["response"]
        return [
            Character(name=char["name"], age=char["age"], gender=char["gender"])
            for char in characters
        ]
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
        return []

def map_characters_to_voices(characters: List[Character]) -> List[CharacterVoiced]:
    available_voices = voices_catalogue[:] 
    voiced_characters = [] 

    # Iterate over characters
    for character in characters:
        matching_voices = [
            voice for voice in available_voices
            if voice.age_group == character.age and voice.gender == character.gender
        ]

        if matching_voices:
            selected_voice = matching_voices[0]
            available_voices.remove(selected_voice)
            voiced_characters.append(CharacterVoiced(character=character, voice=selected_voice))
        else:
            raise ValueError(f"No available voices for {character.name} with age {character.age} and gender {character.gender}")

    return voiced_characters

prompt = Template(
    """
$text

Analyze the following paragraph and identify the speaking characters, their age (young, middle-aged, or elder), and gender (male, or female):

"""
)
