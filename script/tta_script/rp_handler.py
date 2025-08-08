import os
import io
import json
import logging
from typing import BinaryIO

from tta_script.dialogue.types import Script
from tta_script.dialogue.extract import get_script
from tta_script.character.extract import get_characters
from tta_script.text_utils import normalize_quotes
from tta_script.voices import assign_voices

from tta_types.types import (
    WebhookResponse,
    WebhookRequest,
    Response,
    ScriptRequest,
)
from tta_aws.s3 import S3Client

import requests
import runpod


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

s3_client = S3Client()


def _to_json_fileobject(filename: str, script_data: Script) -> BinaryIO:
    json_data = script_data.to_dict()
    json_bytes = json.dumps(json_data, indent=4).encode("utf-8")
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = f"{filename}"
    return file_obj


def _upload_script_result(user_id: str, script_data: Script, chapter_name: str):
    script_file = _to_json_fileobject("script.json", script_data)
    project_script_path = f"{user_id}/{chapter_name}/script.json"
    s3_client.upload_fileobj(f"{PROJECTS_BUCKET}", project_script_path, script_file)
    return str(script_file.name)


def handler(event: dict):
    request = WebhookRequest.model_validate(event["input"])
    request_data = ScriptRequest.model_validate(request.data)

    text = normalize_quotes(request_data.text_content)
    previous_speakers = set(request_data.previous_speakers)

    try:
        speakers = assign_voices(
            characters=get_characters(text, {s.character for s in previous_speakers}),
            voices=request_data.voices,
            previous_speakers=previous_speakers,
        )
        script = get_script(text, speakers)
        script_filename = _upload_script_result(
            request.user_id, script, request_data.chapter_name
        )
        status = "complete"
        message = ""
        data = Response(filename=script_filename, request_word_count=len(text.split()))
    except (ValueError, KeyError, TypeError, RuntimeError) as e:
        logger.exception("Exception occurred during script processing: %s", str(e))
        status = "failed"
        message = str(e)
        data = Response(filename="", request_word_count=0)

    requests.post(
        request.callback,
        json=WebhookResponse(
            user_id=request.user_id,
            event=request.event,
            status=status,
            message=message,
            data=data,
        ).model_dump(),
        timeout=120,
    )


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
