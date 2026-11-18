"""Read a checked script aloud, each line in its character's voice.

The script and cast come from the script step. Every character with lines
needs a voice (CastMember.voice), and every such voice a recorded clip with
its exact transcript, which the speech model clones.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from tta_narration.speech import SpeechModel, VoiceClip
from tta_script.cast import Cast
from tta_script.script import Script, ScriptSegment

# Longer text makes the model more likely to drop or repeat words, so each
# piece it reads stays under this many words, split at clause boundaries.
MAX_WORDS = 40
PIECE_GAP_S = 0.25  # between pieces and lines of one paragraph
PARAGRAPH_GAP_S = 0.7

# Curly quotes made one model skip text; straight ones read the same.
QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})


@dataclass(frozen=True)
class Line:
    """One line of the script read aloud, with the pause before it."""

    id: str  # ScriptSegment.id
    start: float  # seconds into the narration where the line's speech begins
    end: float
    audio: np.ndarray  # float32 mono at the model's sample rate: the pause, then the speech


def narrate(script: Script, cast: Cast, voices: dict[str, VoiceClip], model: SpeechModel) -> Iterator[Line]:
    """The script read aloud a line at a time, in order, each line as soon as
    it is read, so playback can start with the first.

    Raises ValueError straight away, before reading anything, naming every
    character who has lines but no voice and every voice with no clip."""
    lines = [s for s in script.segments if s.text.strip()]
    line_voices = [_voice_name(cast, s.speaker_id) for s in lines]
    _check_voices(cast, lines, line_voices, voices)
    return _read(lines, [voices[v] for v in line_voices if v is not None], model)


def _read(lines: list[ScriptSegment], voices: list[VoiceClip], model: SpeechModel) -> Iterator[Line]:
    sr = model.sample_rate
    position = 0  # samples so far
    for i, (line, voice) in enumerate(zip(lines, voices, strict=True)):
        parts = []
        if i:
            parts.append(_pause(PARAGRAPH_GAP_S if line.paragraph != lines[i - 1].paragraph else PIECE_GAP_S, sr))
        start = position + sum(len(p) for p in parts)
        for j, clip in enumerate(model.say(_split(line.text.translate(QUOTES)), voice)):
            if j:
                parts.append(_pause(PIECE_GAP_S, sr))
            parts.append(clip)
        audio = np.concatenate(parts)
        position += len(audio)
        yield Line(line.id, round(start / sr, 3), round(position / sr, 3), audio)


def _pause(seconds: float, sr: int) -> np.ndarray:
    return np.zeros(int(sr * seconds), dtype=np.float32)


def _voice_name(cast: Cast, speaker_id: str) -> str | None:
    member = cast.get(speaker_id)
    return member.voice if member else None


def _check_voices(
    cast: Cast, lines: list[ScriptSegment], line_voices: list[str | None], voices: dict[str, VoiceClip]
) -> None:
    unvoiced = sorted({_name(cast, s.speaker_id) for s, v in zip(lines, line_voices) if v is None})
    unrecorded = sorted({v for v in line_voices if v is not None and v not in voices})
    problems = []
    if unvoiced:
        problems.append(f"no voice for {', '.join(unvoiced)}")
    if unrecorded:
        problems.append(f"no clip for voices {', '.join(unrecorded)}")
    if problems:
        raise ValueError("; ".join(problems))


def _name(cast: Cast, speaker_id: str) -> str:
    member = cast.get(speaker_id)
    return member.name if member else speaker_id


def _split(text: str) -> list[str]:
    """text in pieces of at most about MAX_WORDS words: at sentence ends,
    then at ; and :, then between commas. A short tail joins the piece before."""
    text = re.sub(r"\s+", " ", text).strip()
    pieces: list[str] = []
    for sentence in re.split(r'(?<=[.!?")])\s+(?=[A-Z"(])', text):
        for part in re.split(r"(?<=[;:])\s+", sentence) if _words(sentence) > MAX_WORDS else [sentence]:
            if _words(part) <= MAX_WORDS:
                pieces.append(part)
                continue
            current: list[str] = []
            for clause in re.split(r"(?<=,)\s+", part):
                if current and _words(" ".join(current + [clause])) > MAX_WORDS:
                    pieces.append(" ".join(current))
                    current = []
                current.append(clause)
            if current:
                pieces.append(" ".join(current))
    merged: list[str] = []
    for piece in pieces:
        if merged and _words(piece) < 6 and _words(merged[-1] + " " + piece) <= MAX_WORDS + 6:
            merged[-1] += " " + piece
        else:
            merged.append(piece)
    return merged


def _words(text: str) -> int:
    return len(text.split())
