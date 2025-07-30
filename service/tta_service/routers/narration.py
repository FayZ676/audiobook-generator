from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, status
from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    SpeechRequestSegment,
    AudiobookJob,
)
from tta_types.script import ScriptData
from tta_service.types import BuildNarrationRequest
from tta_service.config import (
    s3_client,
    SERVICE_API_URL,
    SPEECH_API_URL,
    SPEECH_SERVICE_API_KEY,
    SPEECH_COST_PER_WORD,
    USAGE_LIMIT,
    PROJECTS_BUCKET,
)
from tta_service.utils import send_async_request, update_status, validate_usage
from tta_service.routers.job import get_job_status


router = APIRouter()


@router.post("/narration", status_code=status.HTTP_202_ACCEPTED)
async def build_narration(request: BuildNarrationRequest, bg_tasks: BackgroundTasks):
    script_data = s3_client.get_file(
        PROJECTS_BUCKET, f"{request.user_id}/{request.chapter_name}/script.json"
    ).decode("utf-8")
    speech_segments = ScriptData.model_validate_json(script_data).to_speech_segments()
    validate_usage(
        user_id=request.user_id,
        word_count=sum(len(segment.text.split()) for segment in speech_segments),
        cost_per_word=SPEECH_COST_PER_WORD,
        usage_limit=USAGE_LIMIT,
    )
    existing_job = get_job_status(request.user_id)
    update_status(
        AudiobookJob(
            job_id=request.user_id,
            narration_status="processing",
            script_status=existing_job.script_status if existing_job else None,
            message=None,
            script_started_at=(
                existing_job.script_started_at if existing_job else None
            ),
            narration_started_at=datetime.now(timezone.utc).isoformat(),
        )
    )
    bg_tasks.add_task(
        send_narration_request,
        request.user_id,
        request.chapter_name,
        request.voices,
        speech_segments,
    )
    return f"{request.user_id}/{request.chapter_name}"


@router.get("/narration/{user_id}/{chapter_name}")
def get_narration(user_id: str, chapter_name: str):
    project_narration_path = f"{user_id}/{chapter_name}/narration.mp3"
    if not s3_client.list_files(PROJECTS_BUCKET, project_narration_path):
        return None
    narration_url = s3_client.presigned_url(PROJECTS_BUCKET, project_narration_path)
    return narration_url


@router.delete("/narration/{user_id}/{chapter_name}")
def delete_narration(user_id: str, chapter_name: str):
    project_narration_path = f"{user_id}/{chapter_name}/narration.mp3"
    if not s3_client.list_files(PROJECTS_BUCKET, project_narration_path):
        return
    return s3_client.delete_file(PROJECTS_BUCKET, project_narration_path)


async def send_narration_request(
    user_id: str,
    chapter_name: str,
    voices: list[Voice],
    speech_segments: list[SpeechRequestSegment],
):
    request = WebhookRequest(
        callback=f"{SERVICE_API_URL}/events",
        event="speech",
        user_id=user_id,
        data=SpeechRequest(
            user_id=user_id,
            text=speech_segments,
            voices=voices,
            chapter_name=chapter_name,
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
