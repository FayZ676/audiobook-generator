import json

from tta_types.types import Script, ScriptSegment

from tta_script.dialogue.prompts import label_prompt
from tta_script.dialogue.types import (
    Dialogue,
    TextSegment,
    DialogueLabel,
    DialogueLabelResponse,
)
from tta_script.speakers import Speaker
from tta_script.models.text import generate_text


def get_script(text: str, speakers: set[Speaker]) -> Script:
    dialogues = get_dialogues(get_text_segments(text), speakers)
    script_segments = [
        ScriptSegment(
            id=f"seg-{i:04d}", text=d.text, speaker_alias=d.speaker.first_alias()
        )
        for i, d in enumerate(dialogues)
    ]
    unique_speakers = list(set(d.speaker for d in dialogues))
    return Script(segments=script_segments, speakers=unique_speakers)


def get_dialogues(text_segments: list[TextSegment], speakers: set[Speaker]):
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
    texts: list[TextSegment], speakers: set[Speaker], batch_size: int = 100
):
    labels: list[DialogueLabel] = []
    batches = create_text_batches(texts, batch_size)
    for batch in batches:
        result = label(batch, speakers)
        labels.extend(result)
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


def label(texts: dict[int, TextSegment], speakers: set[Speaker]):
    prompt = label_prompt.substitute(
        text="\n".join([f"{i}. {d}" for i, d in texts.items()]),
        speakers="\n".join([f"- {s.first_alias()}" for s in speakers]),
        num_segments=len(texts),
    )
    response = generate_text("", prompt, DialogueLabelResponse)
    result = [DialogueLabel(**d) for d in json.loads(response)["dialogue"]]
    if len(result) > len(texts):
        raise RuntimeError(
            f"Invalid number of labels returned: "
            f"Expected {len(texts)} (at most), but got {len(result)}."
        )
    return result


def get_text_segments(text: str) -> list[TextSegment]:
    def clean_text(text: str) -> str:
        return text.strip().replace("\n", " ")

    result: list[TextSegment] = []
    paragraphs = [clean_text(p) for p in text.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        if paragraph.count('"') % 2 != 0:
            # TODO: Handle with LLM.
            result.append(TextSegment(paragraph, is_dialogue=False))
        else:
            in_quotes = False
            current_text = ""
            for _, char in enumerate(paragraph):
                if char == '"':
                    if current_text:
                        result.append(
                            TextSegment(current_text.strip(), is_dialogue=in_quotes)
                        )
                        current_text = ""
                    in_quotes = not in_quotes
                else:
                    current_text += char
            if current_text:
                result.append(TextSegment(current_text.strip(), is_dialogue=in_quotes))
    return result
