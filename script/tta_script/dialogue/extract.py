import json
from typing import Literal

from pydantic import BaseModel, create_model

from tta_types.cast import NARRATOR_ID, Cast
from tta_types.script import Script, ScriptSegment
from tta_script.dialogue.prompts import label_prompt
from tta_script.dialogue.types import TextSegment
from tta_script.models.text import generate_text


BATCH_SIZE = 100
# How many already-labelled segments each batch sees, so a conversation that
# crosses a batch boundary keeps track of who is speaking.
CONTEXT_SIZE = 30


def label_script(segments: list[TextSegment], cast: Cast) -> Script:
    """Turn segments into a script, with every segment pointing at a cast member.

    Narration, and dialogue the model didn't label, is read by the narrator."""
    labels: dict[int, str] = {}
    for start in range(0, len(segments), BATCH_SIZE):
        batch = {i: segments[i] for i in range(start, min(start + BATCH_SIZE, len(segments)))}
        context = {
            i: (segments[i], labels.get(i, NARRATOR_ID))
            for i in range(max(0, start - CONTEXT_SIZE), start)
        }
        labels.update(label(batch, cast, context))

    return Script(
        segments=[
            ScriptSegment(
                id=f"seg-{i:04d}",
                text=s.text,
                speaker_id=labels.get(i, NARRATOR_ID) if s.is_dialogue else NARRATOR_ID,
            )
            for i, s in enumerate(segments)
        ]
    )


def label(
    segments: dict[int, TextSegment],
    cast: Cast,
    context: dict[int, tuple[TextSegment, str]] | None = None,
) -> dict[int, str]:
    """Ask the model who speaks each segment. Returns index -> cast member id."""
    context = context or {}
    prompt = label_prompt.substitute(
        context=_render_segments(
            {i: f"{s} -> {speaker}" for i, (s, speaker) in context.items()},
            {i: s.paragraph for i, (s, _) in context.items()},
        )
        or "(start of chapter)",
        text=_render_segments(
            {i: str(s) for i, s in segments.items()},
            {i: s.paragraph for i, s in segments.items()},
        ),
        speakers="\n".join(
            f"- {m.id}: {', '.join(m.names)}" for m in sorted(cast.members, key=_speaker_order)
        ),
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


def _speaker_order(member) -> tuple[int, str]:
    # Narrator first, then c1, c2, ... in a stable order, so prompts repeat
    # exactly and can be cached.
    if member.id == NARRATOR_ID:
        return (0, "")
    return (1, member.id[1:].zfill(6))


def _render_segments(lines: dict[int, str], paragraphs: dict[int, int]) -> str:
    """Number each segment, with a blank line wherever a paragraph ends."""
    rendered: list[str] = []
    for i, line in lines.items():
        if rendered and paragraphs[i] != paragraphs[i - 1]:
            rendered.append("")
        rendered.append(f"{i}. {line}")
    return "\n".join(rendered)


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
