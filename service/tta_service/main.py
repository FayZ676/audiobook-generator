import os
import io
import json
import uuid
from typing import BinaryIO

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    SpeechRequestSegment,
    WebhookResponse,
    SpeechResponse,
    ScriptRequest,
    ScriptResponse,
)
from tta_aws.s3 import S3Client

import requests
from fastapi import FastAPI, UploadFile, BackgroundTasks, status
from fastapi.responses import StreamingResponse


app = FastAPI()


SCRIPT_RESULTS_BUCKET = "tta-script-results"
SPEECH_RESULTS_BUCKET = "tta-speech-results"
TEXT_FILES_BUCKET = "tta-text-files"

SPEECH_SERVICE_API_KEY = os.environ.get("SPEECH_SERVICE_API_KEY")
SPEECH_API_URL = "https://api.runpod.ai/v2/c8kreaii0ep89v/run"
VOICES_API_URL = "http://localhost:8002"
SCRIPT_API_URL = "http://localhost:8003"


s3_client = S3Client()


def _get_voices() -> list[Voice]:
    data = requests.get(VOICES_API_URL + "/voices", timeout=5)
    if data.status_code != 200:
        raise ValueError("Failed to fetch voices from the API")
    return [Voice(**v) for v in data.json()]


@app.post("/script")
async def build_script(
    file: UploadFile,
    narrator_voice_name: str,
    callback_url: str,
    bg_tasks: BackgroundTasks,
):
    job_id = str(uuid.uuid4())
    file_content = await file.read()
    filename = file.filename
    if not filename:
        raise ValueError("Invalid File. Name is required.")
    bg_tasks.add_task(
        send_script_request,
        io.BytesIO(file_content),
        filename,
        narrator_voice_name,
        callback_url,
        job_id,
    )
    return job_id


@app.post("/narration", status_code=status.HTTP_202_ACCEPTED)
async def build_narration(
    script_path: str, callback_url: str, bg_tasks: BackgroundTasks
):
    job_id = str(uuid.uuid4())
    bg_tasks.add_task(send_narration_request, script_path, callback_url, job_id)
    return job_id


@app.post("/webhook")
def webhook(response: WebhookResponse):
    response_type = response.type
    match response_type:
        case "speech":
            speech_data = SpeechResponse.model_validate(response.data)
            narration = s3_client.get_file(SPEECH_RESULTS_BUCKET, speech_data.filename)
            narration_file = StreamingResponse(
                io.BytesIO(narration),
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f'attachment; filename="{speech_data.filename}"',
                },
            )
            # TODO: Send narration file to the client.
        case "script":
            script_data = ScriptResponse.model_validate(response.data)
            script_file = s3_client.get_file(
                SCRIPT_RESULTS_BUCKET, script_data.filename
            )
            # TODO: Send script file to the client.
        case _:
            pass


def send_script_request(
    file: BinaryIO,
    filename: str,
    narrator_voice_name: str,
    callback_url: str,
    job_id: str,
):
    s3_client.upload_fileobj(TEXT_FILES_BUCKET, filename, file)
    request = WebhookRequest(
        internal_callback=f"{SCRIPT_API_URL}/webhook",
        external_callback=callback_url,
        job_id=job_id,
        data=ScriptRequest(
            textfile_name=filename,
            narrator_voice_name=narrator_voice_name,
        ).model_dump(),
    )
    requests.post(
        SCRIPT_API_URL + "/script",
        json=request.model_dump(),
        timeout=5,
    )


def send_narration_request(script_path: str, callback_url: str, job_id: str):
    script_data = s3_client.get_file(SCRIPT_RESULTS_BUCKET, script_path)
    request = WebhookRequest(
        internal_callback=f"{SCRIPT_API_URL}/webhook",
        external_callback=callback_url,
        job_id=job_id,
        data=SpeechRequest(
            title=script_path.rstrip(".json"),
            text=[
                SpeechRequestSegment.model_validate(d) for d in json.loads(script_data)
            ],
            voices=_get_voices(),
        ).model_dump(),
    )
    requests.post(
        SPEECH_API_URL,
        json=request.model_dump(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SPEECH_SERVICE_API_KEY}",
        },
        timeout=5,
    )
