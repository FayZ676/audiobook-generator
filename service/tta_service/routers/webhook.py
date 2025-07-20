from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Literal
from tta_types.types import WebhookResponse, AudiobookJob
from tta_service.utils import update_status, update_logs
from tta_service.routers.job import get_job_status
from tta_service.types import PusherEventDetails


class LogEntry(BaseModel):
    job_type: Literal["script", "speech"]
    cost: float


def calculate_cost(request_word_count: int, channel: str) -> float:
    """
    Calculate cost based on word count and channel type.
    Based on Harry Potter Chapter One analysis:
    - 4600 words total cost = $0.494
    - Cost per word = $0.0001073913043
    """
    cost_per_word = 0.0001073913043
    return request_word_count * cost_per_word


router = APIRouter()


@router.post("/webhook")
async def webhook(response: WebhookResponse):
    existing_job = get_job_status(response.user_id)

    match response.channel:
        case "script-channel":
            script_status = response.status
            script_started_at = existing_job.script_started_at if existing_job else None
            narration_status = None
            narration_started_at = None
        case "narration-channel":
            script_status = None
            script_started_at = None
            narration_status = response.status
            narration_started_at = (
                existing_job.narration_started_at if existing_job else None
            )
        case _:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid channel specified in webhook response.",
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

    # Log cost information when job is complete
    if response.status == "complete" and "request_word_count" in response.data:
        request_word_count = response.data["request_word_count"]
        job_type = "script" if response.channel == "script-channel" else "speech"
        cost = calculate_cost(request_word_count, response.channel)
        
        log_entry = LogEntry(job_type=job_type, cost=cost)
        update_logs(log_entry.model_dump(), response.user_id)
