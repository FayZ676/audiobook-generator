import io
from fastapi import APIRouter, UploadFile, status
from tta_service.config import s3_client, TEXT_FILES_BUCKET
from tta_service.text_extractor import extract_text_from_file


router = APIRouter()


@router.post("/text", status_code=status.HTTP_200_OK)
async def upload_text_file(file: UploadFile):
    if not file.filename:
        raise ValueError("Invalid File. Name is required.")
    file_content = await file.read()
    
    # Extract text from the uploaded file
    extracted_text = extract_text_from_file(file_content, file.filename)
    
    # Store the extracted text as a .txt file
    text_filename = file.filename.rsplit('.', 1)[0] + '.txt'
    text_content_bytes = extracted_text.encode('utf-8')
    s3_client.upload_fileobj(TEXT_FILES_BUCKET, text_filename, io.BytesIO(text_content_bytes))
    
    return text_filename


@router.delete("/text/{filename}")
async def delete_text_file(filename: str):
    if not s3_client.list_files(TEXT_FILES_BUCKET, filename):
        return
    return s3_client.delete_file(TEXT_FILES_BUCKET, filename)