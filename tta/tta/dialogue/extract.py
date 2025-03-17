import json

from tta.dialogue.prompts import sys_prompt, prompt, label_prompt
from tta.dialogue.types import (
    Dialogue,
    DialogueDetails,
    TextSegment,
    ResponseFormat,
    DialogueLabel,
    DialogueLabelResponse,
)
from tta.character.types import SpeakerDetails
from tta.voices import SpeakerVoice
from tta.models.text import generate_text


def get_dialogue_details(
    text: str, speakers_voices: set[SpeakerVoice]
) -> list[DialogueDetails]:
    dialogue = get_dialogue(text, {v.character for v in speakers_voices})
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


# TODO: Remove this.
def get_dialogue(text: str, speakers: set[SpeakerDetails]) -> list[Dialogue]:
    def parse_response(response: str, speakers: set[SpeakerDetails]) -> list[Dialogue]:
        def assign_speaker(speaker: str):
            found = next((s for s in speakers if speaker in s.names), None)
            if not found:
                raise ValueError(
                    f"Speaker '{speaker}' not found in list of provided speakers."
                )
            return found

        result = json.loads(response)
        speeches = [
            Dialogue(
                speaker=assign_speaker(s["speaker"]),
                text=str(s["text"]).strip(),
            )
            for s in result["script"]
        ]
        return speeches
    
    llm_prompt = prompt.substitute(
        text=text, characters=", ".join([s.first_alias() for s in speakers])
    )
    result = generate_text(str(sys_prompt), llm_prompt, ResponseFormat)
    return parse_response(result, speakers)


def get_dialogue_nlp(text: str, speakers: set[SpeakerDetails]):
    segments = split_by_dialogue(text)
    labels = label_dialogue(segments, speakers)
    narrator = SpeakerDetails(frozenset({"Narrator"}), "middle-aged", "male")
    dialogue: list[Dialogue] = []
    label_index = 0
    for seg in segments:
        if seg.dialogue:
            speaker = (
                next((s for s in speakers if s.first_alias() == labels[label_index].speaker), None)
                or narrator
            )
            label_index += 1
        else:
            speaker = narrator
        dialogue.append(Dialogue(speaker, seg.text))
    return dialogue


def label_dialogue(dialogues: list[TextSegment], speakers: set[SpeakerDetails]):
    llm_prompt = label_prompt.substitute(
        text="\n".join([f"{i}\t{d}" for i, d in enumerate(dialogues)]),
        speakers=", ".join([s.first_alias() for s in speakers]),
    )
    response = generate_text("", llm_prompt, DialogueLabelResponse)
    return [
        DialogueLabel(r["index"], r["speaker"])
        for r in json.loads(response)["dialogue"]
    ]


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
