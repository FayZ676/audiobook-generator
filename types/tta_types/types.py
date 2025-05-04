from typing import Literal

from pydantic import BaseModel


class Voice(BaseModel):
    name: str
    age: str
    gender: str
    audio_path: str
    audio_transcript: str


class SpeechRequestSegment(BaseModel):
    text: str
    voice_name: str


class SpeechRequest(BaseModel):
    title: str
    text: list[SpeechRequestSegment]
    voices: list[Voice]


class SpeechResponse(BaseModel):
    filename: str


class ScriptResponse(BaseModel):
    filename: str


class WebhookRequest(BaseModel):
    internal_callback: str
    external_callback: str
    job_id: str
    data: dict


class WebhookResponse(BaseModel):
    job_id: str
    type: Literal["speech", "script"]
    status: str
    message: str
    data: dict
    callback_url: str
