from io import BytesIO

from fastapi import APIRouter, HTTPException, status

from tta_service.types import CreateChapterRequest
from tta_service.config import s3_client, PROJECTS_BUCKET

router = APIRouter()


@router.post("/chapter", status_code=status.HTTP_201_CREATED)
async def create_chapter(request: CreateChapterRequest):
    """Create a new chapter for the user's project"""
    if not s3_client.list_files(PROJECTS_BUCKET, f"{request.user_id}/project.json"):
        raise HTTPException(status_code=404, detail="Project not found")

    chapter_path = f"{request.user_id}/{request.chapter_name}/"
    if s3_client.list_files(PROJECTS_BUCKET, chapter_path):
        raise HTTPException(status_code=409, detail="Chapter already exists")
    s3_client.upload_fileobj(
        PROJECTS_BUCKET,
        f"{chapter_path}.chapter",
        BytesIO(b""),
    )


@router.get("/chapters/{user_id}")
def get_chapters(user_id: str):
    """Get all chapters for a user's project by listing chapter directories"""
    user_path = f"{user_id}/"
    chapters = set()
    for file_path in s3_client.list_files(PROJECTS_BUCKET, user_path):
        relative_path = file_path.removeprefix(user_path)

        if "/" in relative_path:
            chapter_name = relative_path.split("/")[0]
            chapters.add(chapter_name)

    return sorted(list(chapters))


@router.delete(
    "/chapter/{user_id}/{chapter_name}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_chapter(user_id: str, chapter_name: str):
    """Delete a chapter and all its contents"""
    chapter_files = s3_client.list_files(PROJECTS_BUCKET, f"{user_id}/{chapter_name}/")
    for file_path in chapter_files:
        s3_client.delete_file(PROJECTS_BUCKET, file_path)
