"""
Script type adapters for cross-service communication.

This module provides adapters to convert between the canonical script types
(defined in script/tta_script/dialogue/types.py) and service-specific formats.
"""

from typing import List
from pydantic import BaseModel
from tta_types.types import SpeechRequestSegment, Speaker


class ScriptData(BaseModel):
    """
    Script data adapter for narration service.

    This adapter handles the JSON format used for script data storage
    and provides conversion to speech request format.
    """

    segments: List[dict]
    speakers: List[Speaker]

    def to_speech_segments(self) -> List[SpeechRequestSegment]:
        """Convert script data to speech request segments with proper voice mapping."""
        speaker_alias_to_voice = {}
        for speaker in self.speakers:
            for name in speaker.character.names:
                speaker_alias_to_voice[name] = speaker.voice.name

        result: List[SpeechRequestSegment] = []
        for segment in self.segments:
            result.append(
                SpeechRequestSegment(
                    id=segment["id"],
                    text=segment.get("text", ""),
                    voice_name=speaker_alias_to_voice.get(
                        segment.get("speaker_alias", ""),
                        segment.get("speaker_alias", ""),
                    ),
                )
            )
        return result
