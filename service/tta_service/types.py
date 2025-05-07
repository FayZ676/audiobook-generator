from pydantic import BaseModel


class BuildScriptRequest(BaseModel):
    narrator_voice_name: str
    callback_url: str
