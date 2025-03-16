import os
from dataclasses import dataclass

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

from tta.character.types import SpeakerDetails


load_dotenv()


@dataclass(eq=True, frozen=True)
class Voice:
    name: str
    gender: str
    age: str
    voice_id: str


@dataclass(eq=True, frozen=True)
class SpeakerVoice:
    character: SpeakerDetails
    voice: Voice


def get_all_voices() -> list[Voice]:
    client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
    voices = client.voices.get_all()
    return [
        Voice(
            name=str(voice.name),
            voice_id=voice.voice_id,
            age=voice.labels["age"],
            gender=voice.labels["gender"],
        )
        for voice in voices.voices
    ]


def get_voices(speakers: set[SpeakerDetails]) -> set[SpeakerVoice]:
    available_voices = get_all_voices()
    voiced_characters = set()
    for speaker in speakers:
        matching_voices = [
            voice
            for voice in available_voices
            if voice.age == speaker.age and voice.gender == speaker.gender
        ]

        if matching_voices:
            selected_voice = matching_voices[0]
            available_voices.remove(selected_voice)
            voiced_characters.add(
                SpeakerVoice(character=speaker, voice=selected_voice)
            )
        else:
            raise ValueError(
                f"No available voices for {speaker.first_alias()} with age {speaker.age} and gender {speaker.gender}"
            )
    return voiced_characters
