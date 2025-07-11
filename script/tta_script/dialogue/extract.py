import json

from tta_script.dialogue.prompts import label_prompt
from tta_script.dialogue.types import (
    Dialogue,
    TextSegment,
    DialogueLabel,
    DialogueLabelResponse,
    ScriptSegment,
    Script,
)
from tta_script.voices import Speaker
from tta_script.models.text import generate_text


def get_script(
    text: str, speakers_voices: set[Speaker]
) -> Script:
    segments = split_by_dialogue(text)
    narrator_speaker = next(
        (s for s in speakers_voices if "Narrator" in s.character.names),
        None
    )
    if not narrator_speaker:
        raise ValueError("No narrator speaker found in the provided speakers.")
    
    dialogue = build_dialogue(segments, speakers_voices, narrator_speaker)

    script_segments = [
        ScriptSegment(text=d.text, speaker_alias=d.speaker.first_alias())
        for d in dialogue
    ]
    unique_speakers = list({d.speaker for d in dialogue})

    return Script(segments=script_segments, speakers=unique_speakers)


def build_dialogue(
    segments: list[TextSegment],
    speakers: set[Speaker],
    narrator_speaker: Speaker,
):
    label_dict = {
        label.index: label.speaker for label in label_dialogue(segments, speakers)
    }
    dialogue: list[Dialogue] = []

    for i, seg in enumerate(segments):
        if seg.dialogue:
            label_speaker = label_dict.get(i)
            speaker = (
                next(
                    (s for s in speakers if s.first_alias() == label_speaker),
                    None,
                )
                or narrator_speaker
            )
        else:
            speaker = narrator_speaker
        dialogue.append(Dialogue(speaker, seg.text))
    return dialogue


def label_dialogue(
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
    batches = [
        {
            i: enumerated[i]
            for i in range(start, min(start + batch_size, len(enumerated)))
        }
        for start in range(0, len(enumerated), batch_size)
    ]
    return batches


def label(texts: dict[int, TextSegment], speakers: set[Speaker], max_retries: int = 3):
    prompt = label_prompt.substitute(
        text="\n".join([f"{i}. {d}" for i, d in texts.items()]),
        speakers="\n".join([f"- {s.first_alias()}" for s in speakers]),
        num_segments=len(texts),
    )
    for _ in range(max_retries):
        response = generate_text("", prompt, DialogueLabelResponse)
        result = [DialogueLabel(**d) for d in json.loads(response)["dialogue"]]
        if len(result) <= len(texts):
            return result
    raise RuntimeError(
        f"Invalid number of labels returned after {max_retries} retries: "
        f"Expected {len(texts)} (at most), but got more."
    )


def split_by_dialogue(text: str) -> list[TextSegment]:
    def clean_text(text: str) -> str:
        return text.strip().replace("\n", " ").replace("“", '"').replace("”", '"')

    result: list[TextSegment] = []
    paragraphs = [clean_text(p) for p in text.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        if paragraph.count('"') % 2 != 0:
            # TODO: Handle with LLM.
            result.append(TextSegment(paragraph, dialogue=False))
        else:
            in_quotes = False
            current_text = ""
            for _, char in enumerate(paragraph):
                if char == '"':
                    if current_text:
                        result.append(
                            TextSegment(current_text.strip(), dialogue=in_quotes)
                        )
                        current_text = ""
                    in_quotes = not in_quotes
                else:
                    current_text += char
            if current_text:
                result.append(TextSegment(current_text.strip(), dialogue=in_quotes))
    return result
