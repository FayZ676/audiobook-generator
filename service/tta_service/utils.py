import io
import requests
from fastapi import HTTPException, status
from tta_types.types import AudiobookJob, JobStatus
from tta_service.config import s3_client, pusher_client, JOB_STATUS_BUCKET


def send_async_request(url: str, payload: dict, headers: dict):
    try:
        requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=1,
        )
    except requests.exceptions.Timeout:
        pass
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send request: {str(e)}",
        )


def update_status(
    job_details: AudiobookJob,
    pusher_channel: str,
    pusher_event: JobStatus,
    pusher_message: str | None,
):
    if not s3_client.list_files(JOB_STATUS_BUCKET, job_details.job_id):
        create_status(job_details, pusher_channel, pusher_event, pusher_message)
    else:
        file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
        file.name = f"{job_details.job_id}.json"
        s3_client.upload_fileobj(
            JOB_STATUS_BUCKET,
            file.name,
            file,
        )
    pusher_client.trigger(pusher_channel, pusher_event, {"message": pusher_message})


def update_status_without_pusher(job_details: AudiobookJob):
    if not s3_client.list_files(JOB_STATUS_BUCKET, job_details.job_id):
        file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
        file.name = f"{job_details.job_id}.json"
        s3_client.upload_fileobj(
            JOB_STATUS_BUCKET,
            file.name,
            file,
        )
    else:
        file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
        file.name = f"{job_details.job_id}.json"
        s3_client.upload_fileobj(
            JOB_STATUS_BUCKET,
            file.name,
            file,
        )


def create_status(
    job_details: AudiobookJob,
    pusher_channel: str,
    pusher_event: str,
    pusher_message: str | None,
):
    file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
    file.name = f"{job_details.job_id}.json"
    s3_client.upload_fileobj(
        JOB_STATUS_BUCKET,
        file.name,
        file,
    )
    pusher_client.trigger(pusher_channel, pusher_event, {"message": pusher_message})