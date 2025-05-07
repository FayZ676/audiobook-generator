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


class WebhookResponseResultData(BaseModel):
    filename: str


class WebhookResponseResult(BaseModel):
    event: Literal["script", "speech"]
    job_id: str
    status: str
    data: WebhookResponseResultData
