import io
from fastapi import APIRouter, UploadFile, status
from tta_service.config import s3_client, TEXT_FILES_BUCKET
from tta_service.text_extractor import extract_text_from_file


router = APIRouter()


def _convert_and_store_as_txt(file_content: bytes, filename: str) -> str:
    """Extract text from file and store as .txt file in S3."""
    extracted_text = extract_text_from_file(file_content, filename)
    text_filename = filename.rsplit('.', 1)[0] + '.txt'
    text_content_bytes = extracted_text.encode('utf-8')
    s3_client.upload_fileobj(TEXT_FILES_BUCKET, text_filename, io.BytesIO(text_content_bytes))
    return text_filename


@router.post("/text", status_code=status.HTTP_200_OK)
async def upload_text_file(file: UploadFile):
    if not file.filename:
        raise ValueError("Invalid File. Name is required.")
    file_content = await file.read()
    
    return _convert_and_store_as_txt(file_content, file.filename)


@router.delete("/text/{filename}")
async def delete_text_file(filename: str):
    if not s3_client.list_files(TEXT_FILES_BUCKET, filename):
        return
    return s3_client.delete_file(TEXT_FILES_BUCKET, filename)