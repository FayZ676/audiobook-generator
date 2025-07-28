from fastapi import APIRouter, HTTPException
from datetime import datetime

from tta_types.types import WebhookResponse, AudiobookJob, EventType
from tta_service.utils import (
    update_status,
    add_file,
    calculate_cost,
    calculate_user_total_cost,
)
from tta_service.routers.job import get_job_status
from tta_service.types import PusherEventDetails, LogEntry
from tta_service.config import LOGS_BUCKET


router = APIRouter()


def save_log_entry(user_id: str, event: EventType, request_word_count: int):
    cost = calculate_cost(request_word_count, event)
    total = calculate_user_total_cost(user_id=user_id, event=event, current_cost=cost)
    log_entry = LogEntry(event=event, total_cost=total, cost=cost)
    add_file(
        data=log_entry.model_dump(),
        filename=f"{user_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        bucket_name=LOGS_BUCKET,
    )


@router.post("/events")
async def events(response: WebhookResponse):
    existing_job = get_job_status(response.user_id)

    match response.event:
        case "script":
            script_status = response.status
            script_started_at = existing_job.script_started_at if existing_job else None
            narration_status = None
            narration_started_at = None
        case "speech":
            script_status = None
            script_started_at = None
            narration_status = response.status
            narration_started_at = (
                existing_job.narration_started_at if existing_job else None
            )
        case "subscription_reset":
            save_log_entry(response.user_id, "subscription_reset", 0)
            return
        case _:
            raise HTTPException(
                status_code=400, detail=f"Unknown event: {response.event}"
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
            channel=f"{response.user_id}-{response.event}",
            event=response.status,
            message=response.message,
        ),
    )

    if response.status == "complete":
        save_log_entry(
            response.user_id, response.event, response.data.request_word_count
        )
