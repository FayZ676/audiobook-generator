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
    WebhookResponseResult,
    WebhookResponseResultData,
    SpeechResponse,
    ScriptRequest,
    ScriptResponse,
)
from tta_aws.s3 import S3Client

from tta_service.types import BuildScriptRequest, BuildNarrationRequest

import pusher
import requests
from fastapi import FastAPI, UploadFile, BackgroundTasks, status, HTTPException
from fastapi.responses import StreamingResponse


app = FastAPI()


VOICES_AUDIOS_BUCKET = "tta-voices-audios"
VOICES_METADATA_BUCKET = "tta-voices-metadata"
SCRIPT_RESULTS_BUCKET = "tta-script-results"
SPEECH_RESULTS_BUCKET = "tta-speech-results"
TEXT_FILES_BUCKET = "tta-text-files"

SERVICE_API_URL = os.environ.get("SERVICE_API_URL", "")

SPEECH_SERVICE_API_KEY = os.environ.get("SPEECH_SERVICE_API_KEY", "")
SPEECH_API_URL = os.environ.get("SPEECH_API_URL", "")

SCRIPT_SERVICE_API_KEY = os.environ.get("SCRIPT_SERVICE_API_KEY", "")
SCRIPT_API_URL = os.environ.get("SCRIPT_API_URL", "")

PUSHER_APP_ID = os.environ.get("PUSHER_APP_ID", "")
PUSHER_KEY = os.environ.get("PUSHER_KEY", "")
PUSHER_SECRET = os.environ.get("PUSHER_SECRET", "")
PUSHER_CLUSTER = os.environ.get("PUSHER_CLUSTER", "")


s3_client = S3Client()


pusher_client = pusher.Pusher(
    app_id=PUSHER_APP_ID,
    key=PUSHER_KEY,
    secret=PUSHER_SECRET,
    cluster=PUSHER_CLUSTER,
    ssl=True,
)


@app.post("/text", status_code=status.HTTP_200_OK)
async def upload_text_file(user_id: str, file: UploadFile):
    if not file.filename:
        raise ValueError("Invalid File. Name is required.")
    file_content = await file.read()
    filename = f"{user_id}-{file.filename}"
    s3_client.upload_fileobj(TEXT_FILES_BUCKET, filename, io.BytesIO(file_content))
    return filename


@app.delete("/text/{filename}")
async def delete_text_file(filename: str):
    return s3_client.delete_file(TEXT_FILES_BUCKET, filename)


@app.post("/script", status_code=status.HTTP_202_ACCEPTED)
async def build_script(request: BuildScriptRequest, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(
        send_script_request,
        request,
    )
    return request.filename


@app.get("/script/{user_id}")
def get_script(user_id: str):
    if not s3_client.list_files(SCRIPT_RESULTS_BUCKET, user_id):
        return None
    script = s3_client.get_file(f"{SCRIPT_RESULTS_BUCKET}", f"{user_id}.json")
    return json.loads(script)


@app.delete("/script/{filename}")
def delete_script(user_id: str, filename: str):
    s3_client.delete_file(f"{SCRIPT_RESULTS_BUCKET}/{user_id}", filename)


@app.post("/narration", status_code=status.HTTP_202_ACCEPTED)
async def build_narration(request: BuildNarrationRequest, bg_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    bg_tasks.add_task(
        send_narration_request, request.script_path, request.voices, job_id
    )
    return job_id


@app.get("/narration/{user_id}")
def get_narration(user_id: str):
    if not s3_client.list_files(SPEECH_RESULTS_BUCKET, user_id):
        return None
    filename = f"{user_id}.mp3"
    narration_url = s3_client.presigned_url(SPEECH_RESULTS_BUCKET, filename)
    return narration_url


@app.delete("/narration/{filename}")
def delete_narration(filename: str):
    return s3_client.delete_file(SPEECH_RESULTS_BUCKET, filename)


@app.post("/webhook")
async def webhook(response: WebhookResponse):
    response_type = response.type
    match response_type:
        case "speech":
            speech_data = SpeechResponse.model_validate(response.data)
            payload = WebhookResponseResult(
                user_id=response.user_id,
                status="completed",
                data=WebhookResponseResultData(filename=speech_data.filename),
            ).model_dump()
        case "script":
            # TODO: Return the script data.
            script_data = ScriptResponse.model_validate(response.data)
            payload = WebhookResponseResult(
                user_id=response.user_id,
                status="completed",
                data=WebhookResponseResultData(filename=script_data.filename),
            ).model_dump()
        case _:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid response type: {response_type}",
            )
    pusher_client.trigger("job-channel", "job-completed", payload)


@app.get("/voices")
def get_voices():
    voices_metadata = s3_client.list_files(VOICES_METADATA_BUCKET, "")
    voices: list[Voice] = []
    for voice_metadata_key in voices_metadata:
        file_content_bytes = s3_client.get_file(
            VOICES_METADATA_BUCKET, str(voice_metadata_key)
        )
        voice_data = json.loads(file_content_bytes.decode("utf-8"))
        voices.append(Voice.model_validate(voice_data))
    return voices


@app.get("/voices/{voice_id}")
def get_voice(voice_name: str):
    file_content_bytes = s3_client.get_file(
        VOICES_METADATA_BUCKET, f"{voice_name}.json"
    )
    voice = json.loads(file_content_bytes.decode("utf-8"))
    return Voice.model_validate(voice)


@app.post("/voices")
def add_voice(
    name: str, age: str, gender: str, audio_transcript: str, audio_file: UploadFile
):
    def to_json_fileobject(voice: Voice) -> BinaryIO:
        file_obj = io.BytesIO(voice.model_dump_json().encode("utf-8"))
        file_obj.name = f"{voice.name}.json"
        return file_obj

    if not audio_file.filename:
        raise ValueError("Audio file with name is required")

    path = s3_client.upload_fileobj(
        VOICES_AUDIOS_BUCKET, audio_file.filename, audio_file.file
    )
    s3_client.upload_fileobj(
        VOICES_METADATA_BUCKET,
        f"{name}.json",
        to_json_fileobject(
            Voice(
                name=name,
                age=age,
                gender=gender,
                audio_path=path,
                audio_transcript=audio_transcript,
            )
        ),
    )
    return


# TODO: Implement the update_voice function
@app.patch("/voices/{voice_id}")
def update_voice(name: str | None = None, age: str | None = None): ...


def send_script_request(script_request: BuildScriptRequest):
    request = WebhookRequest(
        internal_callback=f"{SERVICE_API_URL}/webhook",
        user_id=script_request.user_id,
        data=ScriptRequest(
            textfile_name=script_request.filename,
            narrator_voice_name=script_request.narrator_voice_name,
        ).model_dump(),
    )
    # NOTE: Add /runsync endpoint when testing locally.
    send_async_request(
        url=f"{SCRIPT_API_URL}/runsync",
        payload={"input": request.model_dump()},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SCRIPT_SERVICE_API_KEY}",
        },
    )


async def send_narration_request(script_path: str, voices: list[Voice], user_id: str):
    script_data = s3_client.get_file(SCRIPT_RESULTS_BUCKET, script_path)
    request = WebhookRequest(
        internal_callback=f"{SERVICE_API_URL}/webhook",
        user_id=user_id,
        data=SpeechRequest(
            title=script_path.rstrip(".json"),
            text=[
                SpeechRequestSegment.model_validate(d) for d in json.loads(script_data)
            ],
            voices=voices,
        ).model_dump(),
    )
    # NOTE: Add /runsync endpoint when testing locally.
    send_async_request(
        url=f"{SPEECH_API_URL}/runsync",
        payload={"input": request.model_dump()},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SPEECH_SERVICE_API_KEY}",
        },
    )


def send_async_request(url: str, payload: dict, headers: dict):
    try:
        requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=1,
        )
    except requests.exceptions.Timeout:
        pass
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send script request: {str(e)}",
        )
