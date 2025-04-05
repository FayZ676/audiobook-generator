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
    labels = label_dialogue(segments, speakers)
    narrator_voice = SpeakerVoice(
        SpeakerDetails(frozenset({"Narrator"}), "middle-aged", "male"),
        Voice("Narrator", "male", "middle-aged", "abc123"),
    )
    speakers_voices.add(narrator_voice)
    dialogue: list[Dialogue] = []
    label_index = 0
    for seg in segments:
        if seg.dialogue:
            speaker = (
                next(
                    (
                        s
                        for s in speakers
                        if s.first_alias() == labels[label_index].speaker
                    ),
                    None,
                )
                or narrator_voice.character
            )
            label_index += 1
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
        if d.speaker.first_alias() in voices
    ]


def label_dialogue(
    texts: list[TextSegment], speakers: set[SpeakerDetails], batch_size: int = 100
):
    labels: list[DialogueLabel] = []
    for batch in create_text_batches(texts, batch_size):
        labels.extend(label(batch, speakers))
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


def label(texts: dict[int, TextSegment], speakers: set[SpeakerDetails]):
    llm_prompt = label_prompt.substitute(
        text="\n".join([f"{i}\t{d}" for i, d in texts.items()]),
        speakers=", ".join([s.first_alias() for s in speakers]),
    )
    response = generate_text("", llm_prompt, DialogueLabelResponse)
    result = [
        DialogueLabel(r["index"], r["speaker"])
        for r in json.loads(response)["dialogue"]
    ]
    dialogue = [t for t in texts.values() if t.dialogue]
    if len(result) != len(dialogue):
        raise ValueError(
            f"Invalid number of labels returned: Expected {len(dialogue)} got {len(result)}"
        )
    return result


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
