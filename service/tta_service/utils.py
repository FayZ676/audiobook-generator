import os
import io
import json
import requests

from fastapi import HTTPException, status
from openai import OpenAI

from tta_types.types import AudiobookJob, EventType
from tta_service.config import (
    s3_client,
    pusher_client,
    JOB_STATUS_BUCKET,
    LOGS_BUCKET,
    SCRIPT_COST_PER_WORD,
    SPEECH_COST_PER_WORD,
)
from tta_service.types import PusherEventDetails, LogEntry


openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


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
        add_file(
            data=job_details.model_dump(),
            filename=f"{job_details.job_id}.json",
            bucket_name=JOB_STATUS_BUCKET,
        )
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


# TODO: Does it make more sense for this to live in the s3 client?
def add_file(data: dict, filename: str, bucket_name: str):
    """Upload a file to the specified S3 bucket."""
    file = io.BytesIO(json.dumps(data).encode("utf-8"))
    file.name = filename
    s3_client.upload_fileobj(
        bucket_name,
        filename,
        file,
    )


def calculate_cost(request_word_count: int, job_type: EventType) -> float:
    match job_type:
        case "script":
            return request_word_count * SCRIPT_COST_PER_WORD
        case "speech":
            return request_word_count * SPEECH_COST_PER_WORD
        case "subscription_reset":
            return 0.0
        case _:
            raise HTTPException(status_code=400, detail=f"Unknown job type: {job_type}")


def get_user_total_cost(user_id: str) -> float:
    """Get the current total cost for a user from their most recent log entry."""
    try:
        all_logs = s3_client.list_files(LOGS_BUCKET, f"{user_id}/")
        most_recent_log = sorted(all_logs)[-1] if all_logs else None
        if not most_recent_log:
            return 0.0

        log_data = s3_client.get_file(LOGS_BUCKET, most_recent_log)
        log_entry = LogEntry.model_validate_json(log_data.decode("utf-8"))
        return log_entry.total_cost
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return 0.0


def calculate_user_total_cost(
    user_id: str, event: EventType, current_cost: float
) -> float:
    """Calculate current cost and new total cost for a user event."""
    if event in ["script", "speech"]:
        total = current_cost + get_user_total_cost(user_id)
    elif event == "subscription_reset":
        total = 0.0
    else:
        raise HTTPException(status_code=400, detail=f"Unknown event type: {event}")

    return total


def validate_usage(
    user_id: str,
    word_count: int,
    cost_per_word: float,
    usage_limit: float,
):
    """Validate that a user's request doesn't exceed their usage limit."""
    current_total = get_user_total_cost(user_id)
    estimated_cost = word_count * cost_per_word
    if (current_total + estimated_cost) > usage_limit:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Request would exceed usage limit. Current: ${current_total:.4f}, Estimated: ${estimated_cost:.4f}, Limit: ${usage_limit:.2f}",
        )


def transcribe_audio(audio: bytes):
    audio_file = io.BytesIO(audio)
    audio_file.name = "audio.mp3"
    transcription = openai_client.audio.transcriptions.create(
        model="gpt-4o-transcribe", file=audio_file
    )
    return transcription.text
