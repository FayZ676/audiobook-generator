from typing import List

from tta_types.types import Voice
from tta_types.script import SpeakerDetails, Age, Gender
from tta_script.dialogue.types import ScriptSegment, Script

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
