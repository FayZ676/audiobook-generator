from tta_types.types import Voice, Speaker, JobStatus, EventType, Age, Gender

from pydantic import BaseModel


class Project(BaseModel):
    user_id: str
    name: str


class LogEntry(BaseModel):
    event: EventType
    cost: float
    total_cost: float


# TODO: We should be using actual types here. ScriptSegment and Speakers
class ScriptPayload(BaseModel):
    segments: list[dict[str, str]]
    speakers: list[dict]


class BuildScriptRequest(BaseModel):
    user_id: str
    text_content: str
    chapter_name: str


class CreateChapterRequest(BaseModel):
    user_id: str
    chapter_name: str


class BuildNarrationRequest(BaseModel):
    user_id: str
    voices: list[Voice]
    chapter_name: str
    segment_ids: list[str] | None = None
    endpoint: str


class NarrationEndpointDetails(BaseModel):
    endpoint: str
    words_per_minute: int


class ScriptEndpointDetails(BaseModel):
    endpoint: str


class AddVoiceRequest(BaseModel):
    name: str
    age: Age
    gender: Gender


class FeedbackRequest(BaseModel):
    message: str
    user_id: str


class UpdateScriptRequest(BaseModel):
    script: ScriptPayload


class PusherEventDetails(BaseModel):
    channel: str  # TODO: Specify types for this
    event: JobStatus
    message: str | None
