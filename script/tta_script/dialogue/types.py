from dataclasses import dataclass

from pydantic import BaseModel

from tta_script.character.types import SpeakerDetails


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
class DialogueDetails(Dialogue):
    voice_name: str

    def __str__(self) -> str:
        return f"{self.speaker.first_alias()}: {self.text}"

    def to_dict(self) -> dict:
        return {
            "speaker": self.speaker.to_dict(),
            "text": self.text,
            "voice_name": self.voice_name,
        }


@dataclass(frozen=True, eq=True)
class TextSegment:
    text: str
    dialogue: bool

    def __str__(self) -> str:
        return f"({'D' if self.dialogue else 'N'}) {self.text}"
