from fastapi import APIRouter, HTTPException, status
from tta_types.types import WebhookResponse, AudiobookJob
from tta_service.utils import update_status
from tta_service.routers.job import get_job_status


router = APIRouter()


@router.post("/webhook")
async def webhook(response: WebhookResponse):
    existing_job = get_job_status(response.user_id)

    if response.channel == "script-channel":
        script_status = response.status
        narration_status = existing_job.narration_status if existing_job else None
        script_started_at = existing_job.script_started_at if existing_job else None
        narration_started_at = existing_job.narration_started_at if existing_job else None
    elif response.channel == "narration-channel":
        script_status = existing_job.script_status if existing_job else None
        narration_status = response.status
        script_started_at = existing_job.script_started_at if existing_job else None
        narration_started_at = existing_job.narration_started_at if existing_job else None
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid channel specified in webhook response.",
        )

    update_status(
        AudiobookJob(
            job_id=response.user_id,
            script_status=script_status,
            narration_status=narration_status,
            message=response.message,
            script_started_at=script_started_at,
            narration_started_at=narration_started_at,
        ),
        pusher_channel=response.channel,
        pusher_event=response.status,
        pusher_message=response.message,
    )