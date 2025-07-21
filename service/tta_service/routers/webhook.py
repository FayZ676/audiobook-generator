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


def calculate_cost(request_word_count: int, job_type: JobType) -> float:
    return (
        request_word_count * SCRIPT_COST_PER_WORD
        if job_type == "script"
        else request_word_count * SPEECH_COST_PER_WORD
    )


router = APIRouter()


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
    # If the job is complete, log the cost and add to S3
    if response.status == "complete" and "request_word_count" in response.data:
        request_word_count = response.data["request_word_count"]
        job_type = "script" if response.channel == "script" else "speech"
        cost = calculate_cost(request_word_count, response.channel)

        log_entry = LogEntry(job_type=job_type, cost=cost)
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        add_file(
            data=log_entry.model_dump(),
            filename=f"{response.user_id}_{current_datetime}_log.json",
            bucket_name=JOB_STATUS_BUCKET,
        )
