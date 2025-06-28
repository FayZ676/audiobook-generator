from typing import Literal, Optional

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
    text_content: str
    narrator_voice_name: str
    voices: list[Voice]


class ScriptResponse(BaseModel):
    filename: str


class WebhookRequest(BaseModel):
    callback: str
    channel: str
    user_id: str
    data: dict


JobStatus = Literal["processing", "complete", "failed"]


class WebhookResponse(BaseModel):
    user_id: str
    channel: str
    status: JobStatus
    message: Optional[str]
    data: dict


class WebhookResponseResultData(BaseModel):
    filename: str


class WebhookResponseResult(BaseModel):
    user_id: str
    status: str
    data: WebhookResponseResultData


class AudiobookJob(BaseModel):
    job_id: str
    script_status: Optional[JobStatus]
    narration_status: Optional[JobStatus]
    message: Optional[str]
    script_started_at: Optional[str] = None
    narration_started_at: Optional[str] = None
