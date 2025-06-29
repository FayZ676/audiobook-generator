from dataclasses import dataclass

from pydantic import BaseModel

from tta_script.character.types import SpeakerDetails
from tta_script.voices import SpeakerVoice


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
    speaker: SpeakerVoice
    text: str





@dataclass(frozen=True, eq=True)
class TextSegment:
    text: str
    dialogue: bool

    def __str__(self) -> str:
        return f"({'D' if self.dialogue else 'N'}) {self.text}"


@dataclass(frozen=True, eq=True)
class ScriptSegment:
    text: str
    speaker_alias: str  # References speaker by first_alias()

    def __str__(self) -> str:
        return f"{self.speaker_alias}: {self.text}"


@dataclass(frozen=True, eq=True) 
class Script:
    segments: list[ScriptSegment]
    speakers: list[SpeakerVoice]  # All unique speakers with voice details

    def to_dict(self) -> dict:
        # Create a lookup for speaker voice by alias
        speaker_voice_map = {speaker.first_alias(): speaker.voice.name for speaker in self.speakers}
        
        return {
            "segments": [
                {
                    "text": segment.text,
                    "speaker_alias": segment.speaker_alias,
                    "voice_name": speaker_voice_map.get(segment.speaker_alias, "")
                }
                for segment in self.segments
            ],
            "speakers": [speaker.to_dict() for speaker in self.speakers],
            "voices": speaker_voice_map,  # Keep for backward compatibility
        }
