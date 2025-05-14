import os
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
import runpod


SCRIPT_RESULTS_BUCKET = os.environ.get("SCRIPT_RESULTS_BUCKET", "")
TEXT_FILES_BUCKET = os.environ.get("TEXT_FILES_BUCKET", "")
VOICES_METADATAS_BUCKET = os.environ.get("VOICE_METADATAS_BUCKET", "")


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
    voices_metadata = s3_client.list_files(VOICES_METADATAS_BUCKET, "")
    voices: list[Voice] = []
    for voice_metadata_key in voices_metadata:
        file_content_bytes = s3_client.get_file(
            VOICES_METADATAS_BUCKET, str(voice_metadata_key)
        )
        voice_data = json.loads(file_content_bytes.decode("utf-8"))
        voices.append(Voice.model_validate(voice_data))
    return voices


def _get_textfile_content(textfile_name: str) -> str:
    file: bytes = s3_client.get_file(TEXT_FILES_BUCKET, textfile_name)
    if not file:
        raise ValueError("File not found")
    return file.decode("utf-8")


def handler(event: dict):
    request = WebhookRequest.model_validate(event["input"])
    data = ScriptRequest.model_validate(request.data)
    script = generate_script(
        text=_get_textfile_content(data.textfile_name),
        voices=_get_voices(),
        narrator_name=data.narrator_voice_name,
    )
    script_file = _to_json_fileobject(request.user_id, script)
    s3_client.upload_fileobj(f"{SCRIPT_RESULTS_BUCKET}", script_file.name, script_file)
    requests.post(
        request.internal_callback,
        json=WebhookResponse(
            user_id=request.user_id,
            type="script",
            status="success",
            message="",
            data=ScriptResponse(filename=script_file.name).model_dump(),
        ).model_dump(),
        timeout=120,
    )


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
