import os
from dataclasses import dataclass

from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Voice:
    name: str
    gender: str
    age_group: str
    voice_id: str


class VoiceCatalogue:
    def __init__(self) -> None:
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

    def get_all_voices(self) -> list[Voice]:
        voices = self.client.voices.get_all()
        return [
            Voice(
                name=voice.name,
                voice_id=voice.voice_id,
                age_group=voice.labels["age"],
                gender=voice.labels["gender"],
            )
            for voice in voices.voices
        ]
