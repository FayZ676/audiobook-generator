from typing import List, Literal
from pydantic import BaseModel
from tta_types.types import SpeechRequestSegment


Age = Literal["young", "middle-aged", "old"]
Gender = Literal["male", "female"]


class ScriptSegment(BaseModel):
    """Represents a single segment of script text with speaker information."""
    text: str
    speaker_alias: str


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
    """Complete script data structure with segments and speakers."""
    segments: List[ScriptSegment]
    speakers: List[ScriptSpeaker]
    
    def to_speech_segments(self) -> List[SpeechRequestSegment]:
        """Convert script data to speech request segments with proper voice mapping."""
        # Create speaker alias to voice name mapping
        speaker_alias_to_voice = {}
        for speaker in self.speakers:
            for name in speaker.names:
                speaker_alias_to_voice[name] = speaker.voice_name
        
        # Transform segments to speech request segments
        return [
            SpeechRequestSegment(
                text=segment.text,
                voice_name=speaker_alias_to_voice.get(segment.speaker_alias, segment.speaker_alias)
            )
            for segment in self.segments
        ]
    
    def to_dict(self) -> dict:
        """Convert to dictionary format for serialization."""
        return {
            "segments": [
                {
                    "text": segment.text,
                    "speaker_alias": segment.speaker_alias,
                }
                for segment in self.segments
            ],
            "speakers": [
                {
                    "names": speaker.names,
                    "voice_name": speaker.voice_name,
                }
                for speaker in self.speakers
            ],
        }


class Script(BaseModel):
    """Script model with extended speaker details for service layer."""
    segments: List[ScriptSegment]
    speakers: List[SpeakerDetails]