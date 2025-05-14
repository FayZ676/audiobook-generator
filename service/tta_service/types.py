from pydantic import BaseModel


class BuildScriptRequest(BaseModel):
    user_id: str
    filename: str
    narrator_voice_name: str
