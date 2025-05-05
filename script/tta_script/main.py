import io
import json
from typing import BinaryIO

from tta_script.dialogue.types import DialogueDetails
from tta_script.script import generate_script

from tta_types.types import (
    Voice,
    WebhookResponse,
    WebhookRequest,
    ScriptResponse,
    ScriptRequest,
)
from tta_aws.s3 import S3Client

import requests
from fastapi import FastAPI


app = FastAPI()


SCRIPT_RESULTS_BUCKET = "tta-script-results"
TEXT_FILES_BUCKET = "tta-text-files"

SCRIPT_API_URL = "http://localhost:8000"
VOICES_API_URL = "http://localhost:8002"


s3_client = S3Client()


def _to_json_fileobject(
    filename: str, dialogue_details: list[DialogueDetails]
) -> BinaryIO:
    json_bytes = json.dumps([d.to_dict() for d in dialogue_details], indent=4).encode(
        "utf-8"
    )
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = f"{filename}.json"
    return file_obj


def _get_voices() -> list[Voice]:
    data = requests.get(VOICES_API_URL + "/voices", timeout=5)
    if data.status_code != 200:
        raise ValueError("Failed to fetch voices from the API")
    return [Voice(**v) for v in data.json()]


def _get_textfile_content(textfile_name: str) -> str:
    file: bytes = s3_client.get_file(TEXT_FILES_BUCKET, textfile_name)
    if not file:
        raise ValueError("File not found")
    return file.decode("utf-8")


@app.post("/script")
async def build_script(request: WebhookRequest):
    data = ScriptRequest.model_validate(request.data)
    script = generate_script(
        text=_get_textfile_content(data.textfile_name),
        voices=_get_voices(),
        narrator_name=data.narrator_voice_name,
    )
    script_file = _to_json_fileobject(data.textfile_name.rstrip(".txt"), script)
    s3_client.upload_fileobj(SCRIPT_RESULTS_BUCKET, script_file.name, script_file)
    requests.post(
        SCRIPT_API_URL + "/webhook",
        json=WebhookResponse(
            job_id=request.job_id,
            type="script",
            status="success",
            message="",
            data=ScriptResponse(filename=script_file.name).model_dump(),
            callback_url=request.external_callback,
        ).model_dump(),
        timeout=5,
    )
