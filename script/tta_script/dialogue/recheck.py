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
