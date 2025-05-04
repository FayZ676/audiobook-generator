from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Voice:
    name: str
    age: str
    gender: str
    audio_path: str
    audio_transcript: str


@dataclass
class SpeechRequest:
    title: str
    text: list[dict[str, str]]
    voices: list[Voice]


@dataclass
class WebhookRequest:
    url: str
    job_id: str
    data: dict
