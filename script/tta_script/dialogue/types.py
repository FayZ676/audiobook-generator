from dataclasses import dataclass

from pydantic import BaseModel

from tta_script.voices import Speaker


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


@dataclass(frozen=True, eq=True)
class ScriptSegment:
    text: str
    speaker_alias: str  # References speaker by first_alias()

    def __str__(self) -> str:
        return f"{self.speaker_alias}: {self.text}"


@dataclass(frozen=True, eq=True)
class Script:
    segments: list[ScriptSegment]
    speakers: list[Speaker]  # All unique speakers with voice details

    def to_dict(self) -> dict:
        return {
            "segments": [
                {
                    "text": segment.text,
                    "speaker_alias": segment.speaker_alias,
                }
                for segment in self.segments
            ],
            "speakers": [speaker.to_dict() for speaker in self.speakers],
        }
