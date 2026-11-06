"""A second opinion from a stronger model on the lines the labeller was least
sure of. Most labelling mistakes are among them, so this is where a stronger
model earns its price; the rest of the script isn't sent for answers.

One request per chapter: the whole chapter as context, with the doubtful
lines listed to answer together. The model isn't shown the first labels, so
where the two agree that is two independent answers, and where they differ
is where a person should look."""

import json
import math

from tta_script.cast import Cast
from tta_script.dialogue.decide import GUIDANCE
from tta_script.dialogue.extract import speaker_labels_format
from tta_script.dialogue.render import render_segments, render_speakers
from tta_script.models.text import generate_text
from tta_script.script import Script

RECHECK_MODEL = "anthropic:claude-opus-5-5"
RECHECK_EFFORT = "medium"
# Share of a chapter's dialogue lines, least confident first, to recheck.
RECHECK_SHARE = 0.2

PROMPT = """\
Below is a chapter of a book, split into numbered segments, and the characters who speak in it.

## Speakers
{speakers}

{guidance}

## Chapter
{chapter}

## Your task
Decide who speaks each of these dialogue segments. Read the whole chapter: \
attributions, who is present, who was addressed, and how the conversation \
alternates. Answer every one, with "index" the segment's number.

{lines}"""


def recheck_script(script: Script, cast: Cast, share: float = RECHECK_SHARE) -> Script:
    """Return script with recheck_speaker_id set on the least confident share
    of its dialogue lines. Lines without a confidence count as least sure."""
    dialogue = [i for i, s in enumerate(script.segments) if s.is_dialogue]
    doubtful = sorted(dialogue, key=lambda i: script.segments[i].confidence or 0.0)
    doubtful = sorted(doubtful[: math.ceil(len(dialogue) * share)])
    if not doubtful:
        return script

    segments = script.segments
    prompt = PROMPT.format(
        speakers=render_speakers(cast),
        guidance=GUIDANCE,
        chapter=render_segments(
            {i: f"({'D' if s.is_dialogue else 'N'}) {s.text}" for i, s in enumerate(segments)},
            {i: s.paragraph for i, s in enumerate(segments)},
        ),
        lines="\n".join(f'{i}. "{segments[i].text}"' for i in doubtful),
    )
    reply = generate_text("", prompt, speaker_labels_format(cast), model_name=RECHECK_MODEL, effort=RECHECK_EFFORT)
    answers = {a["index"]: a["speaker"] for a in json.loads(reply)["dialogue"] if a["index"] in doubtful}
    return Script(
        segments=[s.model_copy(update={"recheck_speaker_id": answers.get(i)}) for i, s in enumerate(segments)]
    )
