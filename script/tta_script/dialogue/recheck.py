"""A second opinion from a stronger model on lines a person asks about.

The whole chapter goes in as context, once per request, with every line
asked about listed together, so asking about a whole chapter costs about the
same as asking about a few lines. The model isn't shown the first labels:
where the two agree that is two independent answers, and where they differ
is where a person should look."""

import json

from tta_script.cast import Cast
from tta_script.dialogue.decide import GUIDANCE
from tta_script.dialogue.extract import speaker_labels_format
from tta_script.dialogue.render import render_segments, render_speakers
from tta_script.models.text import generate_text
from tta_script.script import Script

RECHECK_MODEL = "anthropic:claude-opus-5-5"
RECHECK_EFFORT = "medium"

CHAPTER = """\
Below is a chapter of a book, split into numbered segments, and the characters who speak in it.

## Speakers
{speakers}

{guidance}

## Chapter
{chapter}
"""

QUESTION = """
## Your task
Decide who speaks each of these dialogue segments. Read the whole chapter: \
attributions, who is present, who was addressed, and how the conversation \
alternates. Answer every one, with "index" the segment's number.

{lines}"""


def recheck_lines(script: Script, cast: Cast, indices: list[int], *, cache: bool = False) -> dict[int, str]:
    """The stronger model's speaker for each segment index asked about.

    cache keeps the chapter cached for a few minutes, at a quarter more for
    this request, so further questions about the same chapter cost a
    fraction. Worth it when asking about lines one at a time."""
    indices = sorted(set(indices))
    if not indices:
        return {}
    segments = script.segments
    chapter = CHAPTER.format(
        speakers=render_speakers(cast),
        guidance=GUIDANCE,
        chapter=render_segments(
            {i: f"({'D' if s.is_dialogue else 'N'}) {s.text}" for i, s in enumerate(segments)},
            {i: s.paragraph for i, s in enumerate(segments)},
        ),
    )
    question = QUESTION.format(lines="\n".join(f'{i}. "{segments[i].text}"' for i in indices))
    reply = generate_text(
        "",
        question if cache else chapter + question,
        speaker_labels_format(cast),
        model_name=RECHECK_MODEL,
        effort=RECHECK_EFFORT,
        cached_prefix=chapter if cache else "",
    )
    return {a["index"]: a["speaker"] for a in json.loads(reply)["dialogue"] if a["index"] in indices}


def recheck_segments(script: Script, cast: Cast, segment_ids: list[str]) -> dict[str, str]:
    """The stronger model's speaker for each segment id asked about, or, with
    none given, for every dialogue line a person hasn't checked yet.

    Raises ValueError naming any id the script doesn't have."""
    index = {s.id: i for i, s in enumerate(script.segments)}
    unknown = [s for s in segment_ids if s not in index]
    if unknown:
        raise ValueError(f"No such segments: {', '.join(unknown)}")
    if segment_ids:
        asked = [index[s] for s in segment_ids]
    else:
        asked = [i for i, s in enumerate(script.segments) if s.is_dialogue and not s.reviewed]
    # Lines asked about one or a few at a time come in quick succession, so
    # keep the chapter cached for them.
    answers = recheck_lines(script, cast, asked, cache=bool(segment_ids))
    return {script.segments[i].id: speaker for i, speaker in answers.items()}
