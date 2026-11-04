from dataclasses import dataclass

from pydantic import BaseModel

from tta_types.types import Speaker


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
    speaker: Speaker
    text: str


@dataclass(frozen=True, eq=True)
class TextSegment:
    text: str
    is_dialogue: bool
    # Index of the source paragraph. Fiction starts a new paragraph when the
    # speaker changes, so the labeller needs to know where paragraphs break.
    paragraph: int = 0

    def __str__(self) -> str:
        return f"({'D' if self.is_dialogue else 'N'}) {self.text}"
