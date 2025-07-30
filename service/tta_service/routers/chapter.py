from io import BytesIO

from fastapi import APIRouter, HTTPException, status

from tta_service.types import CreateChapterRequest, Project
from tta_service.config import s3_client, PROJECTS_BUCKET

router = APIRouter()


@router.post("/chapter", status_code=status.HTTP_201_CREATED)
async def create_chapter(request: CreateChapterRequest):
    """Create a new chapter for the user's project"""
    project_path = f"{request.user_id}/project.json"

    if not s3_client.list_files(PROJECTS_BUCKET, project_path):
        raise HTTPException(status_code=404, detail="Project not found")

    project_content = s3_client.get_file(PROJECTS_BUCKET, project_path).decode("utf-8")
    project = Project.model_validate_json(project_content)

    if request.chapter_name in project.chapters:
        raise HTTPException(status_code=409, detail="Chapter already exists")

    project.chapters.append(request.chapter_name)

    s3_client.upload_fileobj(
        PROJECTS_BUCKET,
        project_path,
        BytesIO(project.model_dump_json().encode("utf-8")),
    )


@router.get("/chapters/{user_id}")
def get_chapters(user_id: str):
    """Get all chapters for a user's project"""
    project_path = f"{user_id}/project.json"

    if not s3_client.list_files(PROJECTS_BUCKET, project_path):
        return []

    project_content = s3_client.get_file(PROJECTS_BUCKET, project_path).decode("utf-8")
    project = Project.model_validate_json(project_content)

    return project.chapters


@router.delete(
    "/chapter/{user_id}/{chapter_name}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_chapter(user_id: str, chapter_name: str):
    """Delete a chapter and all its contents"""
    project_path = f"{user_id}/project.json"

    if not s3_client.list_files(PROJECTS_BUCKET, project_path):
        raise HTTPException(status_code=404, detail="Project not found")

    project_content = s3_client.get_file(PROJECTS_BUCKET, project_path).decode("utf-8")
    project = Project.model_validate_json(project_content)

    project.chapters = [ch for ch in project.chapters if ch != chapter_name]

    s3_client.upload_fileobj(
        PROJECTS_BUCKET,
        project_path,
        BytesIO(project.model_dump_json().encode("utf-8")),
    )

    chapter_files = s3_client.list_files(PROJECTS_BUCKET, f"{user_id}/{chapter_name}/")
    for file_path in chapter_files:
        s3_client.delete_file(PROJECTS_BUCKET, file_path)
