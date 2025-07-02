"""
Script type adapters for cross-service communication.

This module provides adapters to convert between the canonical script types
(defined in script/tta_script/dialogue/types.py) and service-specific formats.
"""

from typing import List, Literal
from pydantic import BaseModel
from tta_types.types import SpeechRequestSegment


Age = Literal["young", "middle-aged", "old"]
Gender = Literal["male", "female"]


class ScriptSpeaker(BaseModel):
    """Represents speaker information with names and voice mapping."""

    names: List[str]
    voice_name: str


class SpeakerDetails(BaseModel):
    """Extended speaker information including demographic and audio details."""

    names: List[str]
    age: Age
    gender: Gender
    voice_name: str
    audio_path: str = ""
    audio_transcript: str = ""


class ScriptData(BaseModel):
    """
    Script data adapter for narration service.

    This adapter handles the JSON format used for script data storage
    and provides conversion to speech request format.
    """

    segments: List[dict]
    speakers: List[ScriptSpeaker]

    def to_speech_segments(self) -> List[SpeechRequestSegment]:
        """Convert script data to speech request segments with proper voice mapping."""
        speaker_alias_to_voice = {}
        for speaker in self.speakers:
            for name in speaker.names:
                speaker_alias_to_voice[name] = speaker.voice_name

        return [
            SpeechRequestSegment(
                text=segment.get("text", ""),
                voice_name=speaker_alias_to_voice.get(
                    segment.get("speaker_alias", ""), segment.get("speaker_alias", "")
                ),
            )
            for segment in self.segments
        ]
