from typing import Literal, Optional, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from tta_types.script import SpeakerDetails


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
    user_id: str
    text: list[SpeechRequestSegment]
    voices: list[Voice]
    chapter_name: str


class ScriptRequest(BaseModel):
    text_content: str
    voices: list[Voice]
    chapter_name: str
    previous_speakers: Optional[list["SpeakerDetails"]] = None


class Response(BaseModel):
    filename: str
    request_word_count: int


EventType = Literal["script", "speech", "subscription_reset"]


class WebhookRequest(BaseModel):
    callback: str
    event: EventType
    user_id: str
    data: dict


JobStatus = Literal["processing", "complete", "failed"]


class WebhookResponse(BaseModel):
    user_id: str
    event: EventType
    status: JobStatus
    message: Optional[str]
    data: Response


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
