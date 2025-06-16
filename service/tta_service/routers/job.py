import json
from fastapi import APIRouter
from tta_types.types import AudiobookJob
from tta_service.config import s3_client, JOB_STATUS_BUCKET


router = APIRouter()


@router.get("/job/status/{job_id}")
def get_job_status(job_id: str):
    if not s3_client.list_files(JOB_STATUS_BUCKET, job_id):
        return None
    job_status = s3_client.get_file(JOB_STATUS_BUCKET, f"{job_id}.json")
    return AudiobookJob.model_validate(json.loads(job_status))


@router.delete("/job/status/{filename}")
def delete_job_status(filename: str):
    if not s3_client.list_files(JOB_STATUS_BUCKET, filename):
        return
    s3_client.delete_file(JOB_STATUS_BUCKET, filename)