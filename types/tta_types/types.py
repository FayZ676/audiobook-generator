from typing import Literal

from pydantic import BaseModel


class Voice(BaseModel):
    name: str
    age: str
    gender: str
    audio_path: str
    audio_transcript: str

    model_config = {"frozen": True}


class SpeechRequestSegment(BaseModel):
    text: str
    voice_name: str


class SpeechRequest(BaseModel):
    title: str
    text: list[SpeechRequestSegment]
    voices: list[Voice]


class SpeechResponse(BaseModel):
    filename: str


class ScriptRequest(BaseModel):
    textfile_name: str
    narrator_voice_name: str


class ScriptResponse(BaseModel):
    filename: str


class WebhookRequest(BaseModel):
    internal_callback: str
    user_id: str
    data: dict


class WebhookResponse(BaseModel):
    user_id: str
    type: Literal["speech", "script"]
    status: str
    message: str
    data: dict


class WebhookResponseResultData(BaseModel):
    filename: str


class WebhookResponseResult(BaseModel):
    user_id: str
    status: str
    data: WebhookResponseResultData


class AudiobookJob(BaseModel):
    job_id: str
    status: str
