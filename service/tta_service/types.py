from tta_types.types import JobStatus, Voice, CharacterVoiceMappings
from tta_types.script import Age, Gender

from pydantic import BaseModel


class ScriptPayload(BaseModel):
    segments: list[dict[str, str]]
    speakers: list[dict]


class BuildScriptRequest(BaseModel):
    user_id: str
    text_content: str
    character_voice_mappings: CharacterVoiceMappings | None = None


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
    channel: str
    event: JobStatus
    message: str | None
