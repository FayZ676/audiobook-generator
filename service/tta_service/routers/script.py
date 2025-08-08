import io
import json
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, status
from tta_types.types import WebhookRequest, ScriptRequest, AudiobookJob, Voice, Speaker
from tta_types.script import ScriptData
from tta_service.types import BuildScriptRequest, UpdateScriptRequest
from tta_service.config import (
    s3_client,
    VOICES_BUCKET,
    SERVICE_API_URL,
    SCRIPT_API_URL,
    SCRIPT_SERVICE_API_KEY,
    SCRIPT_COST_PER_WORD,
    USAGE_LIMIT,
    PROJECTS_BUCKET,
)
from tta_service.utils import send_async_request, update_status, validate_usage
from tta_service.routers.job import get_job_status


router = APIRouter()


@router.post("/script", status_code=status.HTTP_202_ACCEPTED)
async def build_script(request: BuildScriptRequest, bg_tasks: BackgroundTasks):
    validate_usage(
        user_id=request.user_id,
        word_count=len(request.text_content.split()),
        cost_per_word=SCRIPT_COST_PER_WORD,
        usage_limit=USAGE_LIMIT,
    )

    existing_job = get_job_status(request.user_id)

    update_status(
        AudiobookJob(
            job_id=request.user_id,
            script_status="processing",
            narration_status=existing_job.narration_status if existing_job else None,
            message=None,
            script_started_at=datetime.now(timezone.utc).isoformat(),
            narration_started_at=(
                existing_job.narration_started_at if existing_job else None
            ),
        )
    )

    bg_tasks.add_task(
        send_script_request,
        request,
    )
    return request.text_content


@router.get("/script/{user_id}/{chapter_name}")
def get_script(user_id: str, chapter_name: str):
    project_script_path = f"{user_id}/{chapter_name}/script.json"
    if s3_client.list_files(PROJECTS_BUCKET, project_script_path):
        script = s3_client.get_file(PROJECTS_BUCKET, project_script_path).decode(
            "utf-8"
        )
        return json.loads(script)
    return None


@router.delete("/script/{user_id}/{chapter_name}")
def delete_script(user_id: str, chapter_name: str):
    project_script_path = f"{user_id}/{chapter_name}/script.json"
    if s3_client.list_files(PROJECTS_BUCKET, project_script_path):
        s3_client.delete_file(PROJECTS_BUCKET, project_script_path)


@router.put("/script/{user_id}/{chapter_name}")
def update_script(user_id: str, chapter_name: str, request: UpdateScriptRequest):
    file_obj = io.BytesIO(json.dumps(request.script.model_dump()).encode("utf-8"))
    s3_client.upload_fileobj(
        PROJECTS_BUCKET, f"{user_id}/{chapter_name}/script.json", file_obj
    )


def send_script_request(script_request: BuildScriptRequest):
    voices = _get_voices(script_request.user_id)
    previous_speakers = _get_previous_speakers(script_request.user_id)

    request = WebhookRequest(
        callback=f"{SERVICE_API_URL}/events",
        event="script",
        user_id=script_request.user_id,
        data=ScriptRequest(
            text_content=script_request.text_content,
            voices=voices,
            chapter_name=script_request.chapter_name,
            previous_speakers=list(previous_speakers),
        ).model_dump(),
    )
    # NOTE: Add /runsync endpoint when testing locally.
    send_async_request(
        url=f"{SCRIPT_API_URL}",
        payload={"input": request.model_dump()},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SCRIPT_SERVICE_API_KEY}",
        },
    )


def _get_voices(user_id: str):
    """Internal function to get voices to avoid circular imports"""
    paths = [
        "metadata/",
        f"{user_id}/metadata/",
    ]
    voices_metadata = [
        file for path in paths for file in s3_client.list_files(VOICES_BUCKET, path)
    ]
    voices: list[Voice] = []
    for voice_metadata_key in voices_metadata:
        file_content = s3_client.get_file(VOICES_BUCKET, voice_metadata_key).decode(
            "utf-8"
        )
        voice_data = json.loads(file_content)
        voices.append(Voice.model_validate(voice_data))
    return voices


def _get_previous_speakers(user_id: str) -> set[Speaker]:
    """Extract speakers from all existing scripts for the user"""
    project_files = s3_client.list_files(PROJECTS_BUCKET, f"{user_id}/")[0]
    previous_speakers: set[Speaker] = set()
    for file in project_files:
        if file.endswith("/script.json"):
            script_content = s3_client.get_file(PROJECTS_BUCKET, file).decode("utf-8")
            script_data = ScriptData.model_validate_json(script_content)
            previous_speakers.update(script_data.speakers)

    return previous_speakers
