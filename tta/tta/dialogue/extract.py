import json

from tta.dialogue.prompts import sys_prompt, prompt
from tta.dialogue.types import Dialogue, DialogueDetails, ResponseFormat
from tta.character.types import SpeakerDetails
from tta.models.text import generate_text


def parse_response(response: str, speakers: set[SpeakerDetails]) -> list[Dialogue]:
    def assign_speaker(speaker: str):
        found = next((s for s in speakers if speaker in s.names), None)
        if not found:
            raise ValueError(f"Speaker '{speaker}' not found in list of provided speakers.")
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


def get_dialogue(text: str, speakers: set[SpeakerDetails]) -> list[Dialogue]:
    llm_prompt = prompt.substitute(
        text=text, characters=", ".join([s.first_alias() for s in speakers])
    )
    result = generate_text(str(sys_prompt), llm_prompt, ResponseFormat)
    return parse_response(result, speakers)


def get_dialogue_details(
    script: list[Dialogue], voices: dict[str, str]
) -> list[DialogueDetails]:
    return [
        DialogueDetails(
            text=dialogue.text,
            speaker=dialogue.speaker,
            voice_id=voices[dialogue.speaker.first_alias()],
        )
        for dialogue in script
        if dialogue.speaker.first_alias() in voices
    ]
