import io
import json
import requests
from fastapi import HTTPException, status
from tta_types.types import AudiobookJob
from tta_service.config import s3_client, pusher_client, JOB_STATUS_BUCKET, LOGS_BUCKET
from tta_service.types import PusherEventDetails


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
    pusher: PusherEventDetails | None = None,
):
    if not s3_client.list_files(JOB_STATUS_BUCKET, job_details.job_id):
        create_status(job_details)
    else:
        file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
        file.name = f"{job_details.job_id}.json"
        s3_client.upload_fileobj(
            JOB_STATUS_BUCKET,
            file.name,
            file,
        )
    if pusher:
        pusher_client.trigger(pusher.channel, pusher.event, {"message": pusher.message})


def create_status(job_details: AudiobookJob):
    file = io.BytesIO(job_details.model_dump_json().encode("utf-8"))
    file.name = f"{job_details.job_id}.json"
    s3_client.upload_fileobj(
        JOB_STATUS_BUCKET,
        file.name,
        file,
    )


def update_logs(log_entry: dict, job_id: str):
    """Store log entry in the logs bucket."""
    file = io.BytesIO(json.dumps(log_entry).encode("utf-8"))
    file.name = f"{job_id}_log.json"
    s3_client.upload_fileobj(
        LOGS_BUCKET,
        file.name,
        file,
    )
