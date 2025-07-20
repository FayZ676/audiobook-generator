import os
import io
import json
from typing import BinaryIO

from tta_script.dialogue.types import Script
from tta_script.dialogue.extract import get_script
from tta_script.character.extract import get_speaker_details
from tta_script.voices import assign_voices

from tta_types.types import (
    WebhookResponse,
    WebhookRequest,
    Response,
    ScriptRequest,
    count_words,
)
from tta_aws.s3 import S3Client

import requests
import runpod


SCRIPT_RESULTS_BUCKET = os.environ.get("SCRIPT_RESULTS_BUCKET", "")


s3_client = S3Client()


def _to_json_fileobject(filename: str, script_data: Script) -> BinaryIO:
    json_data = script_data.to_dict()
    json_bytes = json.dumps(json_data, indent=4).encode("utf-8")
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = f"{filename}.json"
    return file_obj


def _upload_script_result(user_id: str, script_data: Script):
    script_file = _to_json_fileobject(user_id, script_data)
    s3_client.upload_fileobj(f"{SCRIPT_RESULTS_BUCKET}", script_file.name, script_file)
    return str(script_file.name)


def handler(event: dict):
    request = WebhookRequest.model_validate(event["input"])
    data = ScriptRequest.model_validate(request.data)

    text = data.text_content
    speaker_details = get_speaker_details(text)
    voices = data.voices

    if len(speaker_details) > len(voices):
        status = "failed"
        message = "Not enough voices available for the number of speakers in the text."
        data = {}
    else:
        try:
            speaker_voices = assign_voices(
                speakers=speaker_details, voices=voices.copy()
            )
            script = get_script(text, speaker_voices)
            script_filename = _upload_script_result(request.user_id, script)
            word_count = count_words(text)
            status = "complete"
            message = ""
            data = Response(filename=script_filename, request_word_count=word_count).model_dump()
        except ValueError as e:
            status = "failed"
            message = str(e)
            data = {}

    requests.post(
        request.callback,
        json=WebhookResponse(
            user_id=request.user_id,
            channel=request.channel,
            status=status,
            message=message,
            data=data,
        ).model_dump(),
        timeout=120,
    )


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
