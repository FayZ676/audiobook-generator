from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, status
from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    AudiobookJob,
)
from tta_types.script import ScriptData
from tta_service.types import BuildNarrationRequest
from tta_service.config import (
    s3_client,
    SCRIPT_RESULTS_BUCKET,
    SPEECH_RESULTS_BUCKET,
    SERVICE_API_URL,
    SPEECH_API_URL,
    SPEECH_SERVICE_API_KEY,
)
from tta_service.utils import send_async_request, update_status


router = APIRouter()


@router.post("/narration", status_code=status.HTTP_202_ACCEPTED)
async def build_narration(request: BuildNarrationRequest, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(
        send_narration_request, request.script_path, request.voices, request.user_id
    )
    return request.script_path


@router.get("/narration/{filename}")
def get_narration(filename: str):
    if not s3_client.list_files(SPEECH_RESULTS_BUCKET, filename):
        return None
    narration_url = s3_client.presigned_url(SPEECH_RESULTS_BUCKET, filename)
    return narration_url


@router.delete("/narration/{filename}")
def delete_narration(filename: str):
    if not s3_client.list_files(SPEECH_RESULTS_BUCKET, filename):
        return
    return s3_client.delete_file(SPEECH_RESULTS_BUCKET, filename)


async def send_narration_request(script_path: str, voices: list[Voice], user_id: str):
    script_data = s3_client.get_file(SCRIPT_RESULTS_BUCKET, script_path)
    parsed_script = ScriptData.model_validate_json(script_data)
    speech_segments = parsed_script.to_speech_segments()

    request = WebhookRequest(
        callback=f"{SERVICE_API_URL}/webhook",
        channel="narration-channel",
        user_id=user_id,
        data=SpeechRequest(
            title=script_path.rstrip(".json"),
            text=speech_segments,
            voices=voices,
        ).model_dump(),
    )
    # NOTE: Add /runsync endpoint when testing locally.
    send_async_request(
        url=f"{SPEECH_API_URL}",
        payload={"input": request.model_dump()},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SPEECH_SERVICE_API_KEY}",
        },
    )

    update_status(
        AudiobookJob(
            job_id=user_id,
            narration_status="processing",
            script_status=None,
            message=None,
            script_started_at=None,
            narration_started_at=datetime.now(timezone.utc).isoformat(),
        )
    )
