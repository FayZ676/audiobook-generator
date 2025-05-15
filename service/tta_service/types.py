from tta_types.types import Voice

from pydantic import BaseModel


class BuildScriptRequest(BaseModel):
    user_id: str
    filename: str
    narrator_voice_name: str


class BuildNarrationRequest(BaseModel):
    script_path: str
    voices: list[Voice]
