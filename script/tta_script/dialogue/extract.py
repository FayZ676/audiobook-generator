import json
import os
from typing import Literal

from pydantic import BaseModel, create_model

from tta_types.cast import NARRATOR_ID, Cast
from tta_types.script import Script, ScriptSegment
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


def get_text_segments(text: str) -> list[TextSegment]:
    def clean_text(text: str) -> str:
        return text.strip().replace("\n", " ")

    result: list[TextSegment] = []
    paragraphs = [clean_text(p) for p in text.split("\n\n") if p.strip()]
    for p_index, paragraph in enumerate(paragraphs):
        if paragraph.count('"') % 2 != 0:
            # TODO: Handle with LLM.
            result.append(TextSegment(paragraph, False, p_index))
        else:
            in_quotes = False
            current_text = ""
            for _, char in enumerate(paragraph):
                if char == '"':
                    if current_text:
                        result.append(
                            TextSegment(current_text.strip(), in_quotes, p_index)
                        )
                        current_text = ""
                    in_quotes = not in_quotes
                else:
                    current_text += char
            if current_text:
                result.append(TextSegment(current_text.strip(), in_quotes, p_index))
    return result
