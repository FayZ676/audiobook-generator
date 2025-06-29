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
from tta_script.character.types import SpeakerDetails
from tta_script.voices import SpeakerVoice
from tta_script.models.text import generate_text





def get_script(
    text: str, speakers_voices: set[SpeakerVoice], narrator_speaker: SpeakerVoice
) -> Script:
    """
    Extract dialogue as a Script structure with separated speaker metadata.
    
    This is the new preferred method that eliminates SpeakerDetails duplication.
    """
    segments = split_by_dialogue(text)
    
    # Create speakers with voice names included
    speakers_with_voices = {
        SpeakerDetails(
            s.character.names,
            s.character.age,
            s.character.gender,
            s.voice.name
        ) 
        for s in speakers_voices
    }
    
    # Add narrator with voice
    narrator_with_voice = SpeakerDetails(
        narrator_speaker.character.names,
        narrator_speaker.character.age,
        narrator_speaker.character.gender,
        narrator_speaker.voice.name
    )
    speakers_with_voices.add(narrator_with_voice)
    
    dialogue = build_dialogue(segments, speakers_with_voices, narrator_speaker)

    # Create script segments with speaker aliases
    script_segments = [
        ScriptSegment(
            text=d.text,
            speaker_alias=d.speaker.first_alias(),
        )
        for d in dialogue
    ]

    # Get unique speakers from the dialogue (they already have voice names)
    unique_speakers = list({d.speaker for d in dialogue})

    return Script(
        segments=script_segments,
        speakers=unique_speakers,
    )


def build_dialogue(
    segments: list[TextSegment],
    speakers: set[SpeakerDetails],
    narrator_speaker: SpeakerVoice,
):
    label_dict = {
        label.index: label.speaker for label in label_dialogue(segments, speakers)
    }
    dialogue: list[Dialogue] = []
    
    # Create narrator speaker details with voice
    narrator_with_voice = SpeakerDetails(
        narrator_speaker.character.names,
        narrator_speaker.character.age,
        narrator_speaker.character.gender,
        narrator_speaker.voice.name
    )
    
    for i, seg in enumerate(segments):
        if seg.dialogue:
            label_speaker = label_dict.get(i)
            speaker = (
                next(
                    (s for s in speakers if s.first_alias() == label_speaker),
                    None,
                )
                or narrator_with_voice
            )
        else:
            speaker = narrator_with_voice
        dialogue.append(Dialogue(speaker, seg.text))
    return dialogue


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
