from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, eq=True)
class Voice:
    name: str
    age: str
    gender: str
    audio_path: str
    audio_transcript: str


@dataclass
class SpeechRequestSegment:
    text: str
    voice_name: str


@dataclass
class SpeechRequest:
    title: str
    text: list[SpeechRequestSegment]
    voices: list[Voice]


@dataclass
class SpeechResponse:
    filename: str


@dataclass
class WebhookRequest:
    url: str
    job_id: str
    data: dict


@dataclass
class WebhookResponse:
    job_id: str
    type: Literal["speech", "narration"]
    status: str
    message: str
    data: dict
