from fastapi import APIRouter, HTTPException, status
from tta_types.types import WebhookResponse, AudiobookJob
from tta_service.utils import update_status
from tta_service.routers.job import get_job_status
from tta_service.types import PusherEventDetails


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
            # Preserve current_script_filename for script updates
            current_script_filename = existing_job.current_script_filename if existing_job else None
        case "narration-channel":
            script_status = None
            script_started_at = None
            narration_status = response.status
            narration_started_at = (
                existing_job.narration_started_at if existing_job else None
            )
            # Clear current_script_filename when narration completes or fails
            current_script_filename = (
                existing_job.current_script_filename 
                if existing_job and response.status == "processing" 
                else None
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
            current_script_filename=current_script_filename,
        ),
        pusher=PusherEventDetails(
            channel=response.channel,
            event=response.status,
            message=response.message,
        ),
    )
