from tta_types.types import JobStatus, Voice, EventType
from tta_types.script import Age, Gender

from pydantic import BaseModel


class LogEntry(BaseModel):
    event: EventType
    cost: float
    total_cost: float


class ScriptPayload(BaseModel):
    segments: list[dict[str, str]]
    speakers: list[dict]


class BuildScriptRequest(BaseModel):
    user_id: str
    text_content: str


class BuildNarrationRequest(BaseModel):
    user_id: str
    script_path: str
    voices: list[Voice]


class AddVoiceRequest(BaseModel):
    name: str
    age: Age
    gender: Gender
    audio_transcript: str


class FeedbackRequest(BaseModel):
    message: str
    user_id: str


class UpdateScriptRequest(BaseModel):
    script: ScriptPayload


class PusherEventDetails(BaseModel):
    channel: str  # TODO: Specify types for this
    event: JobStatus
    message: str | None
