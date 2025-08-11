from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


Age = Literal["young", "middle-aged", "old"]
Gender = Literal["male", "female"]


class Character(BaseModel):
    names: list[str]
    age: Age
    gender: Gender

    def __hash__(self):
        return hash((tuple(self.names), self.age, self.gender))

    def first_alias(self) -> str:
        return self.names[0] if self.names else ""


class Voice(BaseModel):
    name: str
    age: Age
    gender: Gender
    audio_path: str
    audio_transcript: str

    model_config = ConfigDict(frozen=True)


class Speaker(BaseModel):
    character: Character
    voice: Voice

    model_config = ConfigDict(frozen=True)

    def __hash__(self):
        return hash((self.character, self.voice))

    def first_alias(self) -> str:
        return self.character.first_alias()


class SpeechRequestSegment(BaseModel):
    id: str
    text: str
    voice_name: str


class SpeechRequest(BaseModel):
    user_id: str
    text: list[SpeechRequestSegment]
    voices: list[Voice]
    chapter_name: str


class ScriptRequest(BaseModel):
    text_content: str
    voices: list[Voice]
    chapter_name: str
    previous_speakers: list[Speaker]


class Response(BaseModel):
    filename: str
    request_word_count: int


EventType = Literal["script", "speech", "subscription_reset"]


class WebhookRequest(BaseModel):
    callback: str
    event: EventType
    user_id: str
    data: dict


JobStatus = Literal["processing", "complete", "failed"]


class WebhookResponse(BaseModel):
    user_id: str
    event: EventType
    status: JobStatus
    message: Optional[str]
    data: Response


class WebhookResponseResultData(BaseModel):
    filename: str


class WebhookResponseResult(BaseModel):
    user_id: str
    status: str
    data: WebhookResponseResultData


class AudiobookJob(BaseModel):
    job_id: str
    script_status: Optional[JobStatus]
    narration_status: Optional[JobStatus]
    message: Optional[str]
    script_started_at: Optional[str] = None
    narration_started_at: Optional[str] = None
