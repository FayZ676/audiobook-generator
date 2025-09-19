from datetime import datetime, timezone

import requests
from fastapi import APIRouter, BackgroundTasks, status, HTTPException

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    SpeechRequestSegment,
    AudiobookJob,
)
from tta_types.script import ScriptData
from tta_service.types import BuildNarrationRequest, NarrationEndpointDetails
from tta_service.config import (
    s3_client,
    SERVICE_API_URL,
    SPEECH_API_URL_CPU,
    SPEECH_API_URL_GPU,
    SPEECH_SERVICE_API_KEY,
    SPEECH_COST_PER_WORD,
    USAGE_LIMIT,
    PROJECTS_BUCKET,
)
from tta_service.utils import send_async_request, update_status, validate_usage
from tta_service.routers.job import get_job_status
import json


router = APIRouter()


@router.get("/narration/endpoint")
def get_endpoint() -> NarrationEndpointDetails:
    headers = {"Authorization": f"Bearer {SPEECH_SERVICE_API_KEY}"}
    gpu_response = requests.get(
        url=f"{SPEECH_API_URL_GPU}/health", headers=headers, timeout=5
    )
    cpu_response = requests.get(
        url=f"{SPEECH_API_URL_CPU}/health", headers=headers, timeout=5
    )
    is_gpu_ready = gpu_response.json()["workers"]["ready"] > 0
    is_cpu_ready = cpu_response.json()["workers"]["ready"] > 0
    endpoint = (
        SPEECH_API_URL_GPU
        if is_gpu_ready
        else SPEECH_API_URL_CPU if is_cpu_ready else None
    )
    wpm = 15 if is_gpu_ready else 5 if is_cpu_ready else None
    if not endpoint:
        raise HTTPException(status_code=503, detail="No endpoints are available")
    return NarrationEndpointDetails(endpoint=endpoint, words_per_minute=wpm)  # type: ignore
    # return NarrationEndpointDetails(
    #     endpoint=SPEECH_API_URL_GPU, words_per_minute=5
    # )  # NOTE: For testing


@router.post("/narration", status_code=status.HTTP_202_ACCEPTED)
async def build_narration(request: BuildNarrationRequest, bg_tasks: BackgroundTasks):
    if request.endpoint not in {SPEECH_API_URL_CPU, SPEECH_API_URL_GPU}:
        raise HTTPException(status_code=400, detail="Invalid endpoint")

    script_data = s3_client.get_file(
        PROJECTS_BUCKET, f"{request.user_id}/{request.chapter_name}/script.json"
    ).decode("utf-8")
    all_speech_segments = ScriptData.model_validate_json(
        script_data
    ).to_speech_segments()

    if request.segment_ids:
        requested_set = set(request.segment_ids)
        speech_segments = [s for s in all_speech_segments if s.id in requested_set]
        if len(speech_segments) != len(request.segment_ids):
            raise HTTPException(
                status_code=400, detail="one or more segment_ids are invalid"
            )
    else:
        speech_segments = all_speech_segments

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
            processing_segment_ids=[s.id for s in speech_segments],
        )
    )
    bg_tasks.add_task(
        send_narration_request,
        request.user_id,
        request.chapter_name,
        request.voices,
        speech_segments,
        request.endpoint,
    )
    return f"{request.user_id}/{request.chapter_name}"


@router.get("/narration/{user_id}/{chapter_name}")
def get_narration(user_id: str, chapter_name: str):
    project_narration_path = f"{user_id}/{chapter_name}/audio/narration.mp3"
    if not s3_client.list_files(PROJECTS_BUCKET, project_narration_path):
        return None
    narration_url = s3_client.presigned_url(PROJECTS_BUCKET, project_narration_path)
    return narration_url


@router.get("/narration/{user_id}/{chapter_name}/audio")
def get_narration_manifest(user_id: str, chapter_name: str):
    manifest_key = f"{user_id}/{chapter_name}/audio/manifest.json"
    if not s3_client.list_files(PROJECTS_BUCKET, manifest_key):
        raise HTTPException(status_code=404, detail="manifest not found")
    manifest = json.loads(
        s3_client.get_file(PROJECTS_BUCKET, manifest_key).decode("utf-8")
    )
    narration = manifest.get("narration", {})
    segments = manifest.get("segments", [])
    result = {
        "narration": {
            "key": narration.get("key"),
            "url": s3_client.presigned_url(PROJECTS_BUCKET, narration.get("key")),
        },
        "segments": [
            {
                "id": s.get("id"),
                "index": s.get("index"),
                "key": s.get("key"),
                "url": s3_client.presigned_url(PROJECTS_BUCKET, s.get("key")),
            }
            for s in segments
        ],
    }
    return result


@router.get("/narration/{user_id}/{chapter_name}/segments/{segment_id}")
def get_segment_audio(user_id: str, chapter_name: str, segment_id: str):
    manifest_key = f"{user_id}/{chapter_name}/audio/manifest.json"
    if not s3_client.list_files(PROJECTS_BUCKET, manifest_key):
        raise HTTPException(status_code=404, detail="manifest not found")
    manifest = json.loads(
        s3_client.get_file(PROJECTS_BUCKET, manifest_key).decode("utf-8")
    )
    segments = manifest.get("segments", [])
    match = next((s for s in segments if s.get("id") == segment_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="segment not found")
    key = match.get("key")
    return {"key": key, "url": s3_client.presigned_url(PROJECTS_BUCKET, key)}


@router.delete("/narration/{user_id}/{chapter_name}")
def delete_narration(user_id: str, chapter_name: str):
    project_narration_path = f"{user_id}/{chapter_name}/audio/narration.mp3"
    if not s3_client.list_files(PROJECTS_BUCKET, project_narration_path):
        raise HTTPException(status_code=404, detail="narration not found")
    return s3_client.delete_file(PROJECTS_BUCKET, project_narration_path)


async def send_narration_request(
    user_id: str,
    chapter_name: str,
    voices: list[Voice],
    speech_segments: list[SpeechRequestSegment],
    url: str,
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
        url=f"{url}/run",
        payload={"input": request.model_dump()},
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SPEECH_SERVICE_API_KEY}",
        },
    )
