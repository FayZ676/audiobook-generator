"""A chapter's script: its text in order, each segment pointing at a cast member."""

from pydantic import BaseModel


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
