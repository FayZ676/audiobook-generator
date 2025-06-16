import io
from fastapi import APIRouter, UploadFile, status
from tta_service.config import s3_client, TEXT_FILES_BUCKET


router = APIRouter()


@router.post("/text", status_code=status.HTTP_200_OK)
async def upload_text_file(file: UploadFile):
    if not file.filename:
        raise ValueError("Invalid File. Name is required.")
    file_content = await file.read()
    s3_client.upload_fileobj(TEXT_FILES_BUCKET, file.filename, io.BytesIO(file_content))
    return file.filename


@router.delete("/text/{filename}")
async def delete_text_file(filename: str):
    if not s3_client.list_files(TEXT_FILES_BUCKET, filename):
        return
    return s3_client.delete_file(TEXT_FILES_BUCKET, filename)