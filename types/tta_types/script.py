"""
Script type adapters for cross-service communication.

This module provides adapters to convert between the canonical script types
(defined in script/tta_script/dialogue/types.py) and service-specific formats.
"""

from typing import List
from pydantic import BaseModel
from tta_types.types import SpeechRequestSegment


class ScriptSpeaker(BaseModel):
    """Represents speaker information with names and voice mapping."""

    names: List[str]
    voice_name: str


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
