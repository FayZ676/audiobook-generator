"""Read a checked script aloud, each line in its character's voice.

The script and cast come from the script step. Every character with lines
needs a voice (CastMember.voice): the name of one of the speech model's own
voices, such as "bm_lewis".
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np

from tta_narration.speech import SpeechModel
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
    """One line of the script read aloud. Played in order, each after its
    pause, the lines make the whole narration."""

    id: str  # ScriptSegment.id
    start: float  # seconds into the whole narration where the speech begins
    end: float
    pause: float  # seconds of silence before the speech: longer between paragraphs
    speech: np.ndarray  # float32 mono at the model's sample rate


def narrate(script: Script, cast: Cast, model: SpeechModel) -> Iterator[Line]:
    """The script read aloud a line at a time, in order. The first line comes
    as soon as it is read, so playback can start with it; the rest are read
    a batch at a time (SpeechModel.batch_size), which is much faster on a
    GPU, and come as each batch is done.

    Raises ValueError straight away, before reading anything, naming every
    character who has lines but no voice and every voice the model lacks."""
    lines = [s for s in script.segments if s.text.strip()]
    line_voices = [_voice_name(cast, s.speaker_id) for s in lines]
    _check_voices(cast, lines, line_voices, model.voices)
    return _read(lines, [v for v in line_voices if v is not None], model)


def _read(lines: list[ScriptSegment], voices: list[str], model: SpeechModel) -> Iterator[Line]:
    sr = model.sample_rate
    pieces = [_split(line.text.translate(QUOTES)) for line in lines]
    position = 0  # samples so far
    for group in _groups([len(p) for p in pieces], model.batch_size):
        speeches = _say(model, [pieces[i] for i in group], [voices[i] for i in group])
        for i, speech in zip(group, speeches, strict=True):
            pause = 0.0
            if i:
                pause = PARAGRAPH_GAP_S if lines[i].paragraph != lines[i - 1].paragraph else PIECE_GAP_S
            start = position + int(sr * pause)
            position = start + len(speech)
            yield Line(lines[i].id, round(start / sr, 3), round(position / sr, 3), pause, speech)


def _groups(piece_counts: list[int], batch_size: int) -> Iterator[list[int]]:
    """Indexes of the lines, in order, in groups read together: the first
    line alone, so playback starts as soon as it can, then as many lines as
    make up about batch_size pieces."""
    group: list[int] = []
    pieces = 0
    for i, count in enumerate(piece_counts):
        group.append(i)
        pieces += count
        if i == 0 or pieces >= batch_size:
            yield group
            group, pieces = [], 0
    if group:
        yield group


def _say(model: SpeechModel, pieces: list[list[str]], voices: list[str]) -> list[np.ndarray]:
    """Each line's speech, its pieces read with one call per voice and
    joined with a short pause."""
    clips: dict[tuple[int, int], np.ndarray] = {}  # (line, piece) -> audio
    for voice in dict.fromkeys(voices):
        keys = [(i, j) for i, v in enumerate(voices) if v == voice for j in range(len(pieces[i]))]
        clips.update(zip(keys, model.say([pieces[i][j] for i, j in keys], voice), strict=True))
    gap = _pause(PIECE_GAP_S, model.sample_rate)
    speeches = []
    for i, line_pieces in enumerate(pieces):
        parts = []
        for j in range(len(line_pieces)):
            if j:
                parts.append(gap)
            parts.append(clips[i, j])
        speeches.append(np.concatenate(parts))
    return speeches


def _pause(seconds: float, sr: int) -> np.ndarray:
    return np.zeros(int(sr * seconds), dtype=np.float32)


def _voice_name(cast: Cast, speaker_id: str) -> str | None:
    member = cast.get(speaker_id)
    return member.voice if member else None


def _check_voices(
    cast: Cast, lines: list[ScriptSegment], line_voices: list[str | None], known: frozenset[str]
) -> None:
    unvoiced = sorted({_name(cast, s.speaker_id) for s, v in zip(lines, line_voices) if v is None})
    unknown = sorted({v for v in line_voices if v is not None and v not in known})
    problems = []
    if unvoiced:
        problems.append(f"no voice for {', '.join(unvoiced)}")
    if unknown:
        problems.append(f"the speech model has no voice {', '.join(unknown)}")
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
