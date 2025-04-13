import json

from tta.dialogue.prompts import label_prompt
from tta.dialogue.types import (
    Dialogue,
    DialogueDetails,
    TextSegment,
    DialogueLabel,
    DialogueLabelResponse,
)
from tta.character.types import SpeakerDetails
from tta.voices import SpeakerVoice, Voice
from tta.models.text import generate_text


def get_dialogue_details(text: str, speakers_voices: set[SpeakerVoice]):
    segments = split_by_dialogue(text)
    speakers = {s.character for s in speakers_voices}
    label_dict = {
        label.index: label.speaker for label in label_dialogue(segments, speakers)
    }
    narrator_voice = SpeakerVoice(
        SpeakerDetails(frozenset({"Narrator"}), "middle-aged", "male"),
        Voice("Narrator", "male", "middle-aged", "abc123"),
    )
    speakers_voices.add(narrator_voice)
    dialogue: list[Dialogue] = []
    for i, seg in enumerate(segments):
        if seg.dialogue:
            label_speaker = label_dict.get(i)
            speaker = (
                next(
                    (s for s in speakers if s.first_alias() == label_speaker),
                    None,
                )
                or narrator_voice.character
            )
        else:
            speaker = narrator_voice.character
        dialogue.append(Dialogue(speaker, seg.text))
    voices = {s.character.first_alias(): s.voice.voice_id for s in speakers_voices}
    return [
        DialogueDetails(
            text=d.text,
            speaker=d.speaker,
            voice_id=voices[d.speaker.first_alias()],
        )
        for d in dialogue
        if d.speaker.first_alias() in voices  # TODO: Is this necessary?
    ]


def label_dialogue(
    texts: list[TextSegment], speakers: set[SpeakerDetails], batch_size: int = 100
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


def label(
    texts: dict[int, TextSegment], speakers: set[SpeakerDetails], max_retries: int = 3
):
    dialogue = [t for t in texts.values() if t.dialogue]
    prompt = label_prompt.substitute(
        text="\n".join([f"{i}. {d}" for i, d in texts.items()]),
        speakers="\n".join([f"- {s.first_alias()}" for s in speakers]),
        num_dialogue=len(dialogue),
    )
    for _ in range(max_retries):
        response = generate_text("", prompt, DialogueLabelResponse)
        result = [
            DialogueLabel(r["index"], r["speaker"])
            for r in json.loads(response)["dialogue"]
        ]
        if len(result) <= len(dialogue):
            return result
    raise ValueError(
        f"Invalid number of labels returned after {max_retries} retries: "
        f"Expected {len(dialogue)} (at most), but got more."
    )


def split_by_dialogue(text: str) -> list[TextSegment]:
    result: list[TextSegment] = []
    paragraphs = [p.strip().replace("\n", " ") for p in text.split("\n\n") if p.strip()]
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
