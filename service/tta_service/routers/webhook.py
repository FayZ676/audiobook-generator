from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel
from tta_types.types import WebhookResponse, AudiobookJob, JobType
from tta_service.utils import update_status, add_file
from tta_service.config import (
    JOB_STATUS_BUCKET,
    SCRIPT_COST_PER_WORD,
    SPEECH_COST_PER_WORD,
)
from tta_service.routers.job import get_job_status
from tta_service.types import PusherEventDetails


class LogEntry(BaseModel):
    job_type: JobType
    cost: float


router = APIRouter()


def calculate_cost(request_word_count: int, job_type: JobType) -> float:
    return (
        request_word_count * SCRIPT_COST_PER_WORD
        if job_type == "script"
        else request_word_count * SPEECH_COST_PER_WORD
    )


def log_job_completion(user_id: str, job_type: JobType, request_word_count: int):
    log_entry = LogEntry(
        job_type=job_type,
        cost=calculate_cost(request_word_count, job_type),
    )
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    add_file(
        data=log_entry.model_dump(),
        filename=f"{user_id}/{current_datetime}.json",
        bucket_name=JOB_STATUS_BUCKET,
    )


@router.post("/webhook")
async def webhook(response: WebhookResponse):
    existing_job = get_job_status(response.user_id)

    if response.channel == "script":
        script_status = response.status
        script_started_at = existing_job.script_started_at if existing_job else None
        narration_status = None
        narration_started_at = None
    else:  # NOTE: "speech" is the only other option
        script_status = None
        script_started_at = None
        narration_status = response.status
        narration_started_at = (
            existing_job.narration_started_at if existing_job else None
        )

    update_status(
        job_details=AudiobookJob(
            job_id=response.user_id,
            script_status=script_status,
            narration_status=narration_status,
            message=response.message,
            script_started_at=script_started_at,
            narration_started_at=narration_started_at,
        ),
        pusher=PusherEventDetails(
            channel=response.channel,
            event=response.status,
            message=response.message,
        ),
    )

    if response.status == "complete":
        log_job_completion(
            user_id=response.user_id,
            job_type=response.channel,
            request_word_count=response.data.request_word_count,
        )
