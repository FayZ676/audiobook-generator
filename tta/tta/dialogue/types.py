from dataclasses import dataclass

from pydantic import BaseModel

from tta.character.types import SpeakerDetails


class LLMDialogue(BaseModel):
    speaker: str
    text: str


class ResponseFormat(BaseModel):
    script: list[LLMDialogue]


@dataclass(frozen=True, eq=True)
class Dialogue:
    speaker: SpeakerDetails
    text: str


@dataclass(eq=True, frozen=True)
class DialogueDetails:
    text: str
    speaker: SpeakerDetails
    voice_id: str
