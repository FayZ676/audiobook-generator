import json
from io import BytesIO
from fastapi import APIRouter, HTTPException, status
from tta_service.types import CreateProjectRequest
from tta_service.config import s3_client, PROJECTS_BUCKET
from datetime import datetime, timezone

router = APIRouter()


@router.post("/project", status_code=status.HTTP_201_CREATED)
async def create_project(request: CreateProjectRequest):
    """Create a new project for the user"""
    # TODO: Should this be a custome type?
    project_data = {
        "name": request.project_name,
        "user_id": request.user_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    project_path = f"{request.user_id}/project.json"
    project_data_json = json.dumps(project_data)
    file_obj = BytesIO(project_data_json.encode("utf-8"))
    s3_client.upload_fileobj(PROJECTS_BUCKET, project_path, file_obj)
    return {
        "message": "Project created successfully",
        "project_name": request.project_name,
    }


@router.get("/project/{user_id}")
def get_current_project(user_id: str):
    """Get the current project for a user"""
    project_path = f"{user_id}/project.json"
    if not s3_client.list_files(PROJECTS_BUCKET, project_path):
        return None
    project_data = s3_client.get_file(PROJECTS_BUCKET, project_path)
    return json.loads(project_data)


@router.delete("/project/{user_id}")
def delete_project(user_id: str):
    """Delete a project and all its contents"""
    project_files = s3_client.list_files(PROJECTS_BUCKET, f"{user_id}/")
    for file_path in project_files:
        s3_client.delete_file(PROJECTS_BUCKET, file_path)
    return {"message": "Project deleted successfully"}
