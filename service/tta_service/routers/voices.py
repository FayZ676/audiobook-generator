import io
import json
from typing import BinaryIO

from fastapi import APIRouter, HTTPException, status, Form, UploadFile

from tta_types.types import Voice
from tta_service.types import Age, Gender
from tta_service.config import s3_client, VOICES_BUCKET, pusher_client
from tta_service.utils import transcribe_audio
from tta_service.audio_utils import convert_audio_to_mp3, is_mp3_format


router = APIRouter()


@router.get("/voices/{user_id}")
def get_voices(user_id: str):
    paths = [
        "metadata/",
        f"{user_id}/metadata/",
    ]
    voices_metadata = [
        file for path in paths for file in s3_client.list_files(VOICES_BUCKET, path)
    ]
    voices: list[Voice] = []
    for voice_metadata_key in voices_metadata:
        file_content = s3_client.get_file(VOICES_BUCKET, voice_metadata_key).decode(
            "utf-8"
        )
        voice_data = json.loads(file_content)
        voices.append(Voice.model_validate(voice_data))
    return voices


@router.get("/voices/{user_id}/{voice_name}")
def get_voice(user_id: str, voice_name: str):
    paths = [f"metadata/{voice_name}.json", f"{user_id}/metadata/{voice_name}.json"]
    for path in paths:
        try:
            file_content = s3_client.get_file(VOICES_BUCKET, path).decode("utf-8")
            voice = json.loads(file_content)
            return Voice.model_validate(voice)
        except Exception as e:
            if "NoSuchKey" in str(e):
                continue
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get voice '{voice_name}'",
            )


@router.post("/voices")
def add_voice(
    user_id: str = Form(...),
    name: str = Form(...),
    age: Age = Form(...),
    gender: Gender = Form(...),
    audio_file: UploadFile = Form(...),
):
    def to_json_fileobject(voice: Voice, filename: str) -> BinaryIO:
        file_obj = io.BytesIO(voice.model_dump_json().encode("utf-8"))
        file_obj.name = f"{filename}.json"
        return file_obj

    if not audio_file.filename:
        raise ValueError("Audio file with name is required")

    if is_mp3_format(audio_file.filename):
        mp3_file = audio_file.file
    else:
        mp3_file = convert_audio_to_mp3(audio_file.file)

    mp3_file.seek(0)
    audio_transcript = transcribe_audio(mp3_file.read())
    mp3_file.seek(0)

    name_normalized = name.lower().replace(" ", "_")
    path = f"{user_id}/audio/{name_normalized}.mp3"
    s3_client.upload_fileobj(
        VOICES_BUCKET,
        path,
        mp3_file,
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
    pusher_client.trigger(f"{user_id}-voices", "complete", {"message": "Voice added"})
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


@router.delete("/voices/{user_id}/{voice_name}")
def delete_voice(user_id: str, voice_name: str):
    """Delete a user-created voice"""
    name_normalized = voice_name.lower().replace(" ", "_")

    metadata_path = f"{user_id}/metadata/{name_normalized}.json"
    audio_path = f"{user_id}/audio/{name_normalized}.mp3"

    try:
        s3_client.get_file(VOICES_BUCKET, metadata_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check voice existence: {str(e)}",
        ) from e

    try:
        s3_client.delete_file(VOICES_BUCKET, metadata_path)
        s3_client.delete_file(VOICES_BUCKET, audio_path)
        pusher_client.trigger(
            f"{user_id}-voices", "complete", {"message": "Voice deleted"}
        )
        return {"message": "Voice deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete voice: {str(e)}",
        ) from e
