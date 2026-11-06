"""A chapter's script: its text in order, each segment pointing at a cast member."""

from pydantic import BaseModel

from tta_types.cast import Cast
from tta_types.types import SpeechRequestSegment


class ScriptSegment(BaseModel):
    id: str
    text: str
    speaker_id: str  # CastMember.id
    # How sure the labeller was of speaker_id, from 0 to 1, when it reports
    # that. Low values are the lines worth a person checking.
    confidence: float | None = None

    def __str__(self) -> str:
        return f"{self.speaker_id}: {self.text}"


class Script(BaseModel):
    segments: list[ScriptSegment]

    def to_speech_segments(self, cast: Cast) -> list[SpeechRequestSegment]:
        """Pair every segment with its speaker's voice."""
        result = []
        for segment in self.segments:
            member = cast.get(segment.speaker_id)
            if member is None:
                raise ValueError(f"Segment {segment.id} has unknown speaker {segment.speaker_id!r}")
            result.append(
                SpeechRequestSegment(id=segment.id, text=segment.text, voice_name=member.voice)
            )
        return result
