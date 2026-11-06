"""A chapter's script: its text in order, each segment pointing at a cast member."""

from pydantic import BaseModel


class ScriptSegment(BaseModel):
    id: str
    text: str
    speaker_id: str  # CastMember.id
    is_dialogue: bool = False  # speech, as opposed to narration
    paragraph: int = 0  # index of the source paragraph in the chapter
    # How sure the labeller was of speaker_id, from 0 to 1, when it reports
    # that. Low values are the lines worth a person checking.
    confidence: float | None = None
    # Set by the editor when a person checks the line: the speaker the model
    # gave before any correction, and when it was checked (ISO 8601).
    reviewed: bool = False
    model_speaker_id: str | None = None
    reviewed_at: str | None = None

    def __str__(self) -> str:
        return f"{self.speaker_id}: {self.text}"


class Script(BaseModel):
    segments: list[ScriptSegment]
