from dataclasses import dataclass

from pydantic import BaseModel

from tta_script.speakers import Speaker


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

    def __str__(self) -> str:
        return f"({'D' if self.is_dialogue else 'N'}) {self.text}"


class ScriptSegment(BaseModel):
    id: str
    text: str
    speaker_alias: str  # References speaker by first_alias()

    def __str__(self) -> str:
        return f"{self.speaker_alias}: {self.text}"


class Script(BaseModel):
    segments: list[ScriptSegment]
    speakers: list[Speaker]
