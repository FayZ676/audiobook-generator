import io
import json
import uuid
from typing import BinaryIO

from tta_script.dialogue.types import DialogueDetails
from tta_script.script import generate_script

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    SpeechRequestSegment,
    WebhookResponse,
    SpeechResponse,
)
from tta_aws.s3 import S3Client

import requests
from fastapi import FastAPI, UploadFile, BackgroundTasks, status
from fastapi.responses import StreamingResponse


app = FastAPI()


SCRIPT_RESULTS_BUCKET = "tta-script-results"
SPEECH_RESULTS_BUCKET = "tta-speech-results"

SCRIPT_API_URL = "http://localhost:8000"
SPEECH_API_URL = "http://localhost:8001"
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


@app.post("/script")
def build_script(file: UploadFile, narrator_voice_name: str):
    script = generate_script(
        text=file.file.read().decode("utf-8"),
        voices=_get_voices(),
        narrator_name=narrator_voice_name,
    )
    filename = file.filename
    if not filename:
        raise ValueError("Invalid filename")
    script_file = _to_json_fileobject(filename.rstrip(".txt"), script)
    s3_client.upload_fileobj(SCRIPT_RESULTS_BUCKET, script_file.name, script_file)


@app.post("/narration", status_code=status.HTTP_202_ACCEPTED)
async def build_narration(script_path: str, bg_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    bg_tasks.add_task(send_narration_request, script_path, job_id)
    return job_id


@app.post("/webhook")
def webhook(response: WebhookResponse):
    response_type = response.type
    match response_type:
        case "speech":
            speech_data = SpeechResponse(**response.data)
            narration = s3_client.get_file(SPEECH_RESULTS_BUCKET, speech_data.filename)
            # return StreamingResponse(
            #     io.BytesIO(narration),
            #     media_type="audio/mpeg",
            #     headers={
            #         "Content-Disposition": f'attachment; filename="{speech_data.filename}"',
            #     },
            # )
            # TODO: Send audio file to the client.
            with open(speech_data.filename, "wb") as f:
                f.write(narration)
        case _:
            pass


def send_narration_request(script_path: str, job_id: str):
    script_data = s3_client.get_file(SCRIPT_RESULTS_BUCKET, script_path)
    dialogue_details = [DialogueDetails(**d) for d in json.loads(script_data)]
    request = WebhookRequest(
        url=f"{SCRIPT_API_URL}/webhook",
        job_id=job_id,
        data=SpeechRequest(
            title=script_path.rstrip(".json"),
            text=[
                SpeechRequestSegment(text=d.text, voice_name=d.voice_id)
                for d in dialogue_details
            ],
            voices=_get_voices(),
        ).model_dump(),
    )
    requests.post(
        SPEECH_API_URL + "/speech",
        json=request.model_dump(),
        timeout=5,
    )
