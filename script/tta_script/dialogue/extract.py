import json
import os
from typing import Literal

from pydantic import BaseModel, create_model

from tta_script.cast import NARRATOR_ID, Cast
from tta_script.script import Script, ScriptSegment
from tta_script.dialogue.prompts import label_prompt
from tta_script.dialogue.types import TextSegment
from tta_script.dialogue.decide import DECISIONS_PREFIX, decide_speakers
from tta_script.dialogue.render import render_segments, render_speakers
from tta_script.models.text import generate_text


# Labels dialogue with OpenAI's Decisions API, which also reports each line's
# confidence. Set TTA_LABEL_MODEL to an LLM ("anthropic:claude-haiku-5-5")
# to label with that instead.
DEFAULT_LABEL_MODEL = "openai-decisions:gpt-6-luna"

BATCH_SIZE = 100
# How many already-labelled segments each batch sees, so a conversation that
# crosses a batch boundary keeps track of who is speaking.
CONTEXT_SIZE = 30


def label_script(segments: list[TextSegment], cast: Cast) -> Script:
    """Turn segments into a script, with every segment pointing at a cast member.

    Narration, and dialogue the model didn't label, is read by the narrator.
    TTA_LABEL_MODEL picks the labeller (default: DEFAULT_LABEL_MODEL). An
    "openai-decisions:<model>" labeller also reports each line's confidence."""
    model = os.getenv("TTA_LABEL_MODEL") or DEFAULT_LABEL_MODEL
    confidence: dict[int, float] = {}
    if model.startswith(DECISIONS_PREFIX):
        labels, confidence = decide_speakers(segments, cast, model.removeprefix(DECISIONS_PREFIX))
    else:
        labels = _llm_labels(segments, cast)

    return Script(
        segments=[
            ScriptSegment(
                id=f"seg-{i:04d}",
                text=s.text,
                speaker_id=labels.get(i, NARRATOR_ID) if s.is_dialogue else NARRATOR_ID,
                confidence=confidence.get(i) if s.is_dialogue else None,
            )
            for i, s in enumerate(segments)
        ]
    )


def _llm_labels(segments: list[TextSegment], cast: Cast) -> dict[int, str]:
    labels: dict[int, str] = {}
    for start in range(0, len(segments), BATCH_SIZE):
        batch = {i: segments[i] for i in range(start, min(start + BATCH_SIZE, len(segments)))}
        context = {
            i: (segments[i], labels.get(i, NARRATOR_ID))
            for i in range(max(0, start - CONTEXT_SIZE), start)
        }
        labels.update(label(batch, cast, context))
    return labels


def label(
    segments: dict[int, TextSegment],
    cast: Cast,
    context: dict[int, tuple[TextSegment, str]] | None = None,
) -> dict[int, str]:
    """Ask the model who speaks each segment. Returns index -> cast member id."""
    context = context or {}
    prompt = label_prompt.substitute(
        context=render_segments(
            {i: f"{s} -> {speaker}" for i, (s, speaker) in context.items()},
            {i: s.paragraph for i, (s, _) in context.items()},
        )
        or "(start of chapter)",
        text=render_segments(
            {i: str(s) for i, s in segments.items()},
            {i: s.paragraph for i, s in segments.items()},
        ),
        speakers=render_speakers(cast),
    )
    response = generate_text("", prompt, _response_format(cast))
    return {
        label["index"]: label["speaker"]
        for label in json.loads(response)["dialogue"]
        if label["index"] in segments  # ignore labels for context segments
    }


def _response_format(cast: Cast) -> type[BaseModel]:
    """A response model that only accepts ids of this cast."""
    speaker_ids = tuple(m.id for m in cast.members)
    label_model = create_model(
        "DialogueLabel",
        index=(int, ...),
        speaker=(Literal[speaker_ids], ...),  # type: ignore[valid-type]
    )
    return create_model("DialogueLabels", dialogue=(list[label_model], ...))  # type: ignore[valid-type]


OPEN, CLOSE = "\u201c", "\u201d"
# How far ahead to look for the end of a quote left open at a paragraph's end.
MAX_QUOTED_PARAGRAPHS = 3


def get_text_segments(text: str) -> list[TextSegment]:
    """Split a chapter into narration and dialogue segments, in order.

    Paragraphs are separated by blank lines. Double quotes mark dialogue,
    straight or curly. Quotes inside a quote stay part of it. A quote may run
    over several paragraphs, as a long speech or a song does; it is carried
    into the next paragraph only when a later paragraph shows it continuing,
    so one unclosed quote can't turn the rest of the chapter into dialogue."""
    paragraphs = [_curly_quotes(" ".join(p.split())) for p in text.split("\n\n") if p.strip()]
    segments: list[TextSegment] = []

    def add(segment_text: str, is_dialogue: bool, paragraph: int):
        if segment_text.strip():
            segments.append(TextSegment(segment_text.strip(), is_dialogue, paragraph))

    depth = 0  # 1 inside a quote, 2+ inside a quote within it
    for index, paragraph in enumerate(paragraphs):
        if depth and paragraph.startswith(OPEN):
            paragraph = paragraph[1:]  # marks a speech continuing from the last paragraph
        current = ""
        opened = depth > 0
        for char in paragraph:
            if char == OPEN and depth == 0:
                add(current, False, index)
                current, depth, opened = "", 1, True
            elif char == CLOSE and depth == 1:
                add(current, True, index)
                current, depth = "", 0
            elif char == CLOSE and depth == 0:
                # A closing quote before any opening one: the paragraph began
                # in dialogue and lost its opening quote. Later ones are strays.
                add(current, not opened, index)
                current, opened = "", True
            else:
                depth += char == OPEN
                depth -= char == CLOSE
                current += char
        add(current, depth > 0, index)
        depth = 1 if depth and _quote_continues(paragraphs[index + 1 :]) else 0
    return segments


def _quote_continues(following: list[str]) -> bool:
    """Whether a quote left open at a paragraph's end carries on into the next."""
    for distance, paragraph in enumerate(following[:MAX_QUOTED_PARAGRAPHS]):
        if distance == 0 and paragraph.startswith(OPEN):
            return True  # the usual way a speech carries on into a new paragraph
        first_open, first_close = paragraph.find(OPEN), paragraph.find(CLOSE)
        if first_close != -1 and (first_open == -1 or first_close < first_open):
            return True
        if first_open != -1:
            return False  # a new quote opens first, so the last one was never closed
    return False


def _curly_quotes(paragraph: str) -> str:
    """Turn straight double quotes into opening and closing ones: a quote
    with text after it and a space or bracket (or nothing) before it opens,
    any other closes."""
    if '"' not in paragraph:
        return paragraph
    paragraph = paragraph.replace("\'\'", '"')  # a typo for a closing quote

    def opens(i: int) -> bool:
        before = paragraph[i - 1] if i else " "
        after = paragraph[i + 1] if i + 1 < len(paragraph) else " "
        return (before.isspace() or before in "([") and not after.isspace()

    return "".join(
        (OPEN if opens(i) else CLOSE) if char == '"' else char for i, char in enumerate(paragraph)
    )
