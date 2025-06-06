import os
import io
import json
from typing import BinaryIO

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    SpeechRequestSegment,
    WebhookResponse,
    ScriptRequest,
    AudiobookJob,
)
from tta_aws.s3 import S3Client

from tta_service.types import BuildScriptRequest, BuildNarrationRequest, Age, Gender

import pusher
import requests
from fastapi import FastAPI, UploadFile, BackgroundTasks, status, HTTPException, Form


app = FastAPI()


VOICES_BUCKET = os.environ.get("VOICES_BUCKET", "")
SCRIPT_RESULTS_BUCKET = os.environ.get("SCRIPT_RESULTS_BUCKET", "")
SPEECH_RESULTS_BUCKET = os.environ.get("SPEECH_RESULTS_BUCKET", "")
TEXT_FILES_BUCKET = os.environ.get("TEXT_FILES_BUCKET", "")
JOB_STATUS_BUCKET = os.environ.get("JOB_STATUS_BUCKET", "")

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
async def upload_text_file(file: UploadFile):
    if not file.filename:
        raise ValueError("Invalid File. Name is required.")
    file_content = await file.read()
    s3_client.upload_fileobj(TEXT_FILES_BUCKET, file.filename, io.BytesIO(file_content))
    return file.filename


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


@app.get("/script/{filename}")
def get_script(filename: str):
    if not s3_client.list_files(SCRIPT_RESULTS_BUCKET, filename):
        return None
    script = s3_client.get_file(f"{SCRIPT_RESULTS_BUCKET}", filename)
    return json.loads(script)


@app.delete("/script/{filename}")
def delete_script(filename: str):
    s3_client.delete_file(f"{SCRIPT_RESULTS_BUCKET}", filename)


@app.post("/narration", status_code=status.HTTP_202_ACCEPTED)
async def build_narration(request: BuildNarrationRequest, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(
        send_narration_request, request.script_path, request.voices, request.user_id
    )
    return request.script_path


@app.get("/narration/{filename}")
def get_narration(filename: str):
    if not s3_client.list_files(SPEECH_RESULTS_BUCKET, filename):
        return None
    narration_url = s3_client.presigned_url(SPEECH_RESULTS_BUCKET, filename)
    return narration_url


@app.delete("/narration/{filename}")
def delete_narration(filename: str):
    return s3_client.delete_file(SPEECH_RESULTS_BUCKET, filename)


@app.get("/voices/{user_id}")
def get_voices(user_id: str):
    paths = [
        "metadata/",
        f"metadata/{user_id}/",
    ]
    voices_metadata = [
        file for path in paths for file in s3_client.list_files(VOICES_BUCKET, path)
    ]
    voices: list[Voice] = []
    for voice_metadata_key in voices_metadata:
        file_content_bytes = s3_client.get_file(VOICES_BUCKET, voice_metadata_key)
        voice_data = json.loads(file_content_bytes.decode("utf-8"))
        voices.append(Voice.model_validate(voice_data))
    return voices


@app.get("/voices/{user_id}/{voice_name}")
def get_voice(user_id: str, voice_name: str):
    paths = [f"metadata/{voice_name}.json", f"metadata/{user_id}/{voice_name}.json"]
    for path in paths:
        try:
            file_content_bytes = s3_client.get_file(VOICES_BUCKET, path)
            voice = json.loads(file_content_bytes.decode("utf-8"))
            return Voice.model_validate(voice)
        except Exception as e:
            if "NoSuchKey" in str(e):
                continue
            else:
                return HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get voice '{voice_name}'",
                )
    return None


@app.post("/voices")
def add_voice(
    user_id: str = Form(...),
    name: str = Form(...),
    age: Age = Form(...),
    gender: Gender = Form(...),
    audio_transcript: str = Form(...),
    audio_file: UploadFile = Form(...),
):
    def to_json_fileobject(voice: Voice) -> BinaryIO:
        file_obj = io.BytesIO(voice.model_dump_json().encode("utf-8"))
        file_obj.name = f"{voice.name}.json"
        return file_obj

    if not audio_file.filename:
        raise ValueError("Audio file with name is required")

    path = s3_client.upload_fileobj(
        VOICES_BUCKET, f"{user_id}/audio/{audio_file.filename}", audio_file.file
    )
    s3_client.upload_fileobj(
        VOICES_BUCKET,
        f"{user_id}/metadata/{name}.json",
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


@app.get("/job/status/{job_id}")
def get_job_status(job_id: str):
    if not s3_client.list_files(JOB_STATUS_BUCKET, job_id):
        return None
    job_status = s3_client.get_file(JOB_STATUS_BUCKET, f"{job_id}.json")
    return AudiobookJob.model_validate(json.loads(job_status))


@app.post("/webhook")
async def webhook(response: WebhookResponse):
    match response.type:
        case "speech":
            channel = "narration-channel"
            event = "narration-update"
        case "script":
            channel = "script-channel"
            event = "script-update"
    update_status(
        AudiobookJob(
            job_id=response.user_id, script_status=None, narration_status=None
        ),
        channel,
        event,
    )
    update_status(
        AudiobookJob(
            job_id=response.user_id, script_status=None, narration_status=None
        ),
        "job-channel",
        "job-update",
    )


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
    update_status(
        AudiobookJob(
            job_id=script_request.user_id,
            script_status="processing",
            narration_status=None,
        ),
        "job-channel",
        "job-update",
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
    update_status(
        AudiobookJob(job_id=user_id, narration_status="processing", script_status=None),
        "job-channel",
        "job-update",
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


# TODO: Is there always a status? Should we delete it at any point?
def update_status(job_details: AudiobookJob, pusher_channel: str, pusher_event: str):
    if not s3_client.list_files(JOB_STATUS_BUCKET, job_details.job_id):
        create_status(job_details, pusher_channel, pusher_event)
    else:
        file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
        file.name = f"{job_details.job_id}.json"
        s3_client.upload_fileobj(
            JOB_STATUS_BUCKET,
            file.name,
            file,
        )
    pusher_client.trigger(pusher_channel, pusher_event, {})


def create_status(job_details: AudiobookJob, pusher_channel: str, pusher_event: str):
    file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
    file.name = f"{job_details.job_id}.json"
    s3_client.upload_fileobj(
        JOB_STATUS_BUCKET,
        file.name,
        file,
    )
    pusher_client.trigger(pusher_channel, pusher_event, {})
