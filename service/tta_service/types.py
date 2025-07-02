from tta_types.types import Voice
from tta_types.script import Age, Gender

# TODO: We shouldn't import types from tta_script directly here.
from tta_script.dialogue.types import Script

from pydantic import BaseModel


class BuildScriptRequest(BaseModel):
    user_id: str
    text_content: str
    narrator_voice_name: str


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
    script: Script
