import json

from tta_types.script import Script, ScriptSegment

from tta_script.dialogue.prompts import label_prompt
from tta_script.dialogue.types import (
    Dialogue,
    TextSegment,
    DialogueLabel,
    DialogueLabelResponse,
)
from tta_script.speakers import Speaker
from tta_script.models.text import generate_text


def dialogue_to_script(dialogue: list[Dialogue]) -> Script:
    script_segments = [
        ScriptSegment(
            id=f"seg-{i:04d}", text=d.text, speaker_alias=d.speaker.first_alias()
        )
        for i, d in enumerate(dialogue)
    ]
    unique_speakers = list(set(d.speaker for d in dialogue))
    return Script(segments=script_segments, speakers=unique_speakers)


def get_dialogues(
    text_segments: list[TextSegment], speakers: set[Speaker]
) -> list[Dialogue]:
    narrator = next(s for s in speakers if "Narrator" in s.character.names)
    label_dict = {
        label.index: label.speaker
        for label in assign_speakers_to_dialogue(text_segments, speakers)
    }

    dialogues: list[Dialogue] = []
    for i, segment in enumerate(text_segments):
        if segment.is_dialogue:
            speaker = (
                next(
                    (s for s in speakers if s.first_alias() == label_dict.get(i)),
                    None,
                )
                or narrator
            )
        else:
            speaker = narrator
        dialogues.append(Dialogue(speaker, segment.text))

    return dialogues


def assign_speakers_to_dialogue(
    texts: list[TextSegment],
    speakers: set[Speaker],
    batch_size: int = 100,
    context_size: int = 30,
):
    """Label segments batch by batch. Each batch also sees the last
    context_size segments before it, with their labels, so a conversation
    that crosses a batch boundary keeps track of who is speaking."""
    labels: list[DialogueLabel] = []
    for batch in create_text_batches(texts, batch_size):
        start = min(batch)
        labelled = {l.index: l.speaker for l in labels}
        context = {
            i: (texts[i], labelled.get(i, "Narrator"))
            for i in range(max(0, start - context_size), start)
        }
        labels.extend(label(batch, speakers, context))
    return labels


def create_text_batches(texts: list[TextSegment], batch_size: int):
    enumerated = dict(enumerate(texts))
    return [
        {
            i: enumerated[i]
            for i in range(start, min(start + batch_size, len(enumerated)))
        }
        for start in range(0, len(enumerated), batch_size)
    ]


def label(
    texts: dict[int, TextSegment],
    speakers: set[Speaker],
    context: dict[int, tuple[TextSegment, str]] | None = None,
):
    context = context or {}
    prompt = label_prompt.substitute(
        context=_render_segments(
            {i: f"{s} -> {speaker}" for i, (s, speaker) in context.items()},
            {i: s.paragraph for i, (s, _) in context.items()},
        )
        or "(start of chapter)",
        text=_render_segments(
            {i: str(s) for i, s in texts.items()},
            {i: s.paragraph for i, s in texts.items()},
        ),
        speakers="\n".join([f"- {s.first_alias()}" for s in speakers]),
    )
    response = generate_text("", prompt, DialogueLabelResponse)
    # Ignore any labels the model gives to the context segments.
    result = [
        DialogueLabel(**d)
        for d in json.loads(response)["dialogue"]
        if d["index"] in texts
    ]
    if len(result) > len(texts):
        raise RuntimeError(
            f"Invalid number of labels returned: "
            f"Expected {len(texts)} (at most), but got {len(result)}."
        )
    return result


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
