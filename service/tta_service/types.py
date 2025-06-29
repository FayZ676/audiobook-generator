from typing import List

from tta_types.types import Voice
from tta_script.character.types import Age, Gender

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


class SpeakerDetails(BaseModel):
    names: List[str]
    age: Age
    gender: Gender
    voice_name: str
    audio_path: str
    audio_transcript: str


class ScriptSegment(BaseModel):
    text: str
    speaker_alias: str


class Script(BaseModel):
    segments: List[ScriptSegment]
    speakers: List[SpeakerDetails]


class FeedbackRequest(BaseModel):
    message: str
    user_id: str


class UpdateScriptRequest(BaseModel):
    script: Script
