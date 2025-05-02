import io
import json
from dataclasses import asdict
from typing import BinaryIO

from tta_script.dialogue.types import DialogueDetails
from tta_script.script import generate_script

from tta_types.types import Voice

from tta_aws.s3 import S3Client

from fastapi import FastAPI, UploadFile


app = FastAPI()


SCRIPT_RESULTS_BUCKET = "tta-script-results"


@app.post("/script")
def build_script(file: UploadFile, voices: list[Voice], narrator_voice_name: str):
    script = generate_script(
        text=file.file.read().decode("utf-8"),
        voices=voices,
        narrator_name=narrator_voice_name,
    )
    filename = file.filename
    if not filename:
        raise ValueError("Invalid filename")
    script_file = _to_json_fileobject(filename.rstrip(".txt"), script)
    S3Client().upload_fileobj(SCRIPT_RESULTS_BUCKET, script_file.name, script_file)


def _to_json_fileobject(
    filename: str, dialogue_details: list[DialogueDetails]
) -> BinaryIO:
    json_bytes = json.dumps([asdict(d) for d in dialogue_details], indent=4).encode(
        "utf-8"
    )
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = f"{filename}.json"
    return file_obj
