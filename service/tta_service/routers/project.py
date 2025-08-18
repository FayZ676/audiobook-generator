from io import BytesIO
from fastapi import APIRouter, status
from tta_service.types import Project
from tta_service.config import s3_client, PROJECTS_BUCKET, JOB_STATUS_BUCKET

router = APIRouter()


@router.post("/project", status_code=status.HTTP_201_CREATED)
async def create_project(request: Project):
    """Create a new project for the user"""
    project_path = f"{request.user_id}/project.json"
    project_data_json = request.model_dump_json()
    file_obj = BytesIO(project_data_json.encode("utf-8"))
    s3_client.upload_fileobj(PROJECTS_BUCKET, project_path, file_obj)
    return {
        "message": "Project created successfully",
        "project_name": request.name,
    }


@router.get("/project/{user_id}")
def get_current_project(user_id: str):
    """Get the current project for a user"""
    project_path = f"{user_id}/project.json"
    if not s3_client.list_files(PROJECTS_BUCKET, project_path):
        return None
    project_content = s3_client.get_file(PROJECTS_BUCKET, project_path).decode("utf-8")
    project = Project.model_validate_json(project_content)
    return project


@router.delete("/project/{user_id}")
def delete_project(user_id: str):
    """Delete a project and all its contents"""
    project_files = s3_client.list_files(PROJECTS_BUCKET, f"{user_id}/")
    for file_path in project_files:
        s3_client.delete_file(PROJECTS_BUCKET, file_path)

    job_status_file = f"{user_id}.json"
    if s3_client.list_files(JOB_STATUS_BUCKET, job_status_file):
        s3_client.delete_file(JOB_STATUS_BUCKET, job_status_file)

    return {"message": "Project deleted successfully"}
