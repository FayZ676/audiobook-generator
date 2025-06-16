import io
import json
from typing import BinaryIO
from fastapi import APIRouter, HTTPException, status, Form, UploadFile
from tta_types.types import Voice
from tta_service.types import Age, Gender
from tta_service.config import s3_client, pusher_client, VOICES_BUCKET


router = APIRouter()


@router.get("/voices/{user_id}")
def get_voices(user_id: str):
    paths = [
        "metadata/",
        f"metadata/{user_id}/",
    ]
    voices_metadata = [
        file for path in paths for file in s3_client.list_files(VOICES_BUCKET, path)
    ]
    voices: list[Voice] = []
    for voice_metadata_key in voices_metadata:
        file_content_bytes = s3_client.get_file(VOICES_BUCKET, voice_metadata_key)
        voice_data = json.loads(file_content_bytes.decode("utf-8"))
        voices.append(Voice.model_validate(voice_data))
    return voices


@router.get("/voices/{user_id}/{voice_name}")
def get_voice(user_id: str, voice_name: str):
    paths = [f"metadata/{voice_name}.json", f"metadata/{user_id}/{voice_name}.json"]
    for path in paths:
        try:
            file_content_bytes = s3_client.get_file(VOICES_BUCKET, path)
            voice = json.loads(file_content_bytes.decode("utf-8"))
            return Voice.model_validate(voice)
        except Exception as e:
            if "NoSuchKey" in str(e):
                continue
            else:
                return HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get voice '{voice_name}'",
                )
    return None


@router.post("/voices")
def add_voice(
    user_id: str = Form(...),
    name: str = Form(...),
    age: Age = Form(...),
    gender: Gender = Form(...),
    audio_transcript: str = Form(...),
    audio_file: UploadFile = Form(...),
):
    def to_json_fileobject(voice: Voice, filename: str) -> BinaryIO:
        file_obj = io.BytesIO(voice.model_dump_json().encode("utf-8"))
        file_obj.name = f"{filename}.json"
        return file_obj

    if not audio_file.filename:
        raise ValueError("Audio file with name is required")

    name_normalized = name.lower().replace(" ", "_")
    path = s3_client.upload_fileobj(
        VOICES_BUCKET,
        f"{user_id}/audio/{name_normalized}.{audio_file.filename.split(".")[-1]}",
        audio_file.file,
    )
    s3_client.upload_fileobj(
        VOICES_BUCKET,
        f"{user_id}/metadata/{name_normalized}.json",
        to_json_fileobject(
            voice=Voice(
                name=name,
                age=age,
                gender=gender,
                audio_path=path,
                audio_transcript=audio_transcript,
            ),
            filename=name_normalized,
        ),
    )

    pusher_client.trigger("voices-channel", "complete", {"user_id": user_id})

    return


@router.get("/voices/{user_id}/{voice_name}/audio")
def get_voice_audio_url(user_id: str, voice_name: str):
    """Get presigned URL for voice audio file"""
    audio_paths = [
        f"audio/{voice_name}.mp3",
        f"{user_id}/audio/{voice_name}.mp3",
    ]

    for path in audio_paths:
        try:
            s3_client.get_file(VOICES_BUCKET, path)
            return s3_client.presigned_url(VOICES_BUCKET, path)
        except Exception as e:
            if "NoSuchKey" not in str(e):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to get audio URL: {str(e)}",
                ) from e

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Voice audio '{voice_name}' not found",
    )


@router.patch("/voices/{voice_id}")
def update_voice(name: str | None = None, age: str | None = None): ...