from typing import Literal, Dict, List, Any

from tta_types.types import Voice

from pydantic import BaseModel


type Age = Literal["young", "middle-aged", "old"]


type Gender = Literal["male", "female"]


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
    script: Dict[str, Any]  # New Script format only
