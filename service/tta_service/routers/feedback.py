import io
import json
from datetime import datetime
from fastapi import APIRouter
from tta_service.types import FeedbackRequest
from tta_service.config import s3_client, FEEDBACK_BUCKET


router = APIRouter()


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    timestamp = datetime.now().isoformat()
    filename = f"{request.user_id}_{timestamp}.json"

    feedback_data = request.model_dump()
    feedback_data["timestamp"] = timestamp

    file_obj = io.BytesIO(json.dumps(feedback_data, indent=2).encode("utf-8"))
    file_obj.name = filename

    s3_client.upload_fileobj(FEEDBACK_BUCKET, filename, file_obj)

    return {"status": "success", "filename": filename}