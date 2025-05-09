from pydantic import BaseModel


class BuildScriptRequest(BaseModel):
    filename: str
    narrator_voice_name: str
    callback_url: str
