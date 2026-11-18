"""Read a checked script aloud, each line in its character's voice.

The script and cast come from the script step. Every character with lines
needs a voice (CastMember.voice), and every such voice a recorded clip with
its exact transcript, which the speech model clones.
"""

import re
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
class LineTiming:
    id: str  # ScriptSegment.id
    start: float  # seconds into the narration
    end: float


@dataclass
class Narration:
    audio: np.ndarray  # float32 mono
    sample_rate: int
    lines: list[LineTiming]  # every line with text, in order

    @property
    def duration(self) -> float:
        return len(self.audio) / self.sample_rate


def narrate(script: Script, cast: Cast, voices: dict[str, VoiceClip], model: SpeechModel) -> Narration:
    """The whole script as one recording, with where each line starts and ends.

    Raises ValueError, before reading anything, naming every character who
    has lines but no voice, and every voice with no clip."""
    lines = [s for s in script.segments if s.text.strip()]
    line_voices = [_voice_name(cast, s.speaker_id) for s in lines]
    _check_voices(cast, lines, line_voices, voices)

    pieces = [_split(s.text.translate(QUOTES)) for s in lines]
    return _join(lines, _read_by_voice(pieces, line_voices, voices, model), model.sample_rate)


def _join(lines: list[ScriptSegment], audio: list[list[np.ndarray]], sr: int) -> Narration:
    """Each line's pieces in order, with pauses between, timing each line."""
    out: list[np.ndarray] = []
    timings: list[LineTiming] = []
    position = 0

    def pause(seconds: float) -> None:
        nonlocal position
        out.append(np.zeros(int(sr * seconds), dtype=np.float32))
        position += len(out[-1])

    for i, line in enumerate(lines):
        if i:
            pause(PARAGRAPH_GAP_S if line.paragraph != lines[i - 1].paragraph else PIECE_GAP_S)
        start = position
        for j, clip in enumerate(audio[i]):
            if j:
                pause(PIECE_GAP_S)
            out.append(clip)
            position += len(clip)
        timings.append(LineTiming(line.id, round(start / sr, 3), round(position / sr, 3)))
    return Narration(np.concatenate(out) if out else np.zeros(0, dtype=np.float32), sr, timings)


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


def _read_by_voice(
    pieces: list[list[str]], line_voices: list[str | None], voices: dict[str, VoiceClip], model: SpeechModel
) -> list[list[np.ndarray]]:
    """Audio for every piece of every line, asking the model for all of one
    voice's pieces at once so it can batch them."""
    audio: list[list[np.ndarray]] = [[] for _ in pieces]
    for name in dict.fromkeys(v for v in line_voices if v is not None):
        mine = [(i, text) for i, v in enumerate(line_voices) if v == name for text in pieces[i]]
        for (i, _), clip in zip(mine, model.say([text for _, text in mine], voices[name]), strict=True):
            audio[i].append(clip)
    return audio


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
