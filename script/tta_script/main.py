import io
import json
from dataclasses import asdict
from typing import BinaryIO

from tta_script.character.extract import get_speaker_details
from tta_script.dialogue.extract import get_dialogue_details
from tta_script.dialogue.types import DialogueDetails
from tta_script.voices import assign_voices
from tta_script.character.types import SpeakerDetails
from tta_script.voices import SpeakerVoice

from tta_types.types import Voice

from tta_aws.s3 import S3Client


SCRIPT_RESULTS_BUCKET = "tta-script-results"


def to_json_fileobject(
    filename: str, dialogue_details: list[DialogueDetails]
) -> BinaryIO:
    json_bytes = json.dumps([asdict(d) for d in dialogue_details], indent=4).encode(
        "utf-8"
    )
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = f"{filename}.json"
    return file_obj


def generate_script(title: str, text: str, voices: list[Voice], narrator_name: str):
    speaker_voices = assign_voices(get_speaker_details(text), voices=voices)
    narrator_voice = SpeakerVoice(
        SpeakerDetails(frozenset({"Narrator"}), "middle-aged", "male"),
        next(voice for voice in voices if voice.name == narrator_name),
    )
    dialogue_details = get_dialogue_details(text, speaker_voices, narrator_voice)
    file = to_json_fileobject(title, dialogue_details)
    S3Client().upload_fileobj(SCRIPT_RESULTS_BUCKET, file.name, file)


if __name__ == "__main__":
    import requests
    from pathlib import Path

    def get_text(filename: str) -> str:
        with open(
            f"{Path(__file__).parent}/../tests/text/{filename}", "r", encoding="utf-8"
        ) as f:
            return f.read()

    def get_voices_from_api() -> list[Voice]:
        response = requests.get("http://localhost:8000/voices")
        return [Voice(**voice) for voice in response.json()]

    voices: list[Voice] = get_voices_from_api()
    generate_script(
        title="harrypotter-sample-tiny",
        text=get_text("harrypotter-sample-tiny.txt"),
        voices=voices,
        narrator_name="Jim Dale",
    )
