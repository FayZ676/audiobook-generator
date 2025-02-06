import os
from dataclasses import dataclass

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

from tta.character import Character


load_dotenv()


@dataclass(eq=True, frozen=True)
class Voice:
    name: str
    gender: str
    age_group: str
    voice_id: str


@dataclass(eq=True, frozen=True)
class CharacterVoiced:
    character: Character
    voice: Voice


class VoiceCatalogue:
    def __init__(self) -> None:
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def get_all_voices(self) -> list[Voice]:
        voices = self.client.voices.get_all()
        return [
            Voice(
                name=str(voice.name),
                voice_id=voice.voice_id,
                age_group=voice.labels["age"],
                gender=voice.labels["gender"],
            )
            for voice in voices.voices
        ]


def map_characters_to_voices(characters: set[Character]) -> set[CharacterVoiced]:
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
