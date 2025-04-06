from dataclasses import dataclass

from pydantic import BaseModel

from tta.character.types import SpeakerDetails


class LLMDialogue(BaseModel):
    speaker: str
    text: str


@dataclass(frozen=True, eq=True)
class DialogueLabel:
    index: int
    speaker: str


class DialogueLabelResponse(BaseModel):
    dialogue: list[DialogueLabel]


@dataclass(frozen=True, eq=True)
class Dialogue:
    speaker: SpeakerDetails
    text: str


@dataclass(eq=True, frozen=True)
class DialogueDetails:
    text: str
    speaker: SpeakerDetails
    voice_id: str

    def __str__(self) -> str:
        return f"{self.speaker.first_alias()}: {self.text}"


@dataclass(frozen=True, eq=True)
class TextSegment:
    text: str
    dialogue: bool

    def __str__(self) -> str:
        return f"({'D' if self.dialogue else 'N'}) {self.text}"
