import os
from io import BytesIO
import logging

import requests
import runpod

from tta_f5.client import F5Client, SegmentId, SpeechAudioPath

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    WebhookResponse,
    Response,
)
from tta_aws.s3 import S3Client

from tta_speech.audio_utils import concat_audio_from_files, audio_file_to_bytesio
from tta_speech.data_utils import download_audio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")
VOICES_BUCKET = os.environ.get("VOICES_BUCKET", "")


s3 = S3Client()


def upload_narration_segments(
    user_id: str,
    chapter_name: str,
    segments: dict[SegmentId, SpeechAudioPath],
) -> None:
    """Generate audio for segments and upload to S3."""
    for seg_id, _segment in segments.items():
        s3.upload_fileobj(
            bucket_name=PROJECTS_BUCKET,
            file_name=f"{user_id}/{chapter_name}/audio/segments/{seg_id}.wav",
            file=audio_file_to_bytesio(segments[seg_id]),
        )


def download_all_segments(user_id: str, chapter_name: str) -> list[str]:
    """Download all segment audio files for a chapter and return ordered file paths."""
    segment_keys = s3.list_files(
        PROJECTS_BUCKET, f"{user_id}/{chapter_name}/audio/segments/"
    )
    ordered_file_paths = []
    for segment_key in sorted(
        segment_keys, key=lambda k: int(k.split("/")[-1].split(".")[0].split("-")[-1])
    ):
        temp_path = f"/tmp/{segment_key.split("/")[-1]}"
        with open(temp_path, "wb") as f:
            f.write(s3.get_file(PROJECTS_BUCKET, segment_key))
        ordered_file_paths.append(temp_path)
    return ordered_file_paths


def build_final_narration(
    user_id: str, chapter_name: str, file_paths: list[str]
) -> str:
    """Concatenate segment files and upload final narration to S3."""
    narration_key = f"{user_id}/{chapter_name}/audio/narration.mp3"
    if file_paths:
        final_narration = concat_audio_from_files(
            file_paths=file_paths, audio_format="wav"
        )
        s3.upload_fileobj(PROJECTS_BUCKET, narration_key, BytesIO(final_narration))
    return narration_key


def download_voices(voices: list[Voice], voice_save_path: str) -> list[Voice]:
    return [
        voice.model_copy(
            update={
                "audio_path": download_audio(
                    audio_path=voice.audio_path,
                    voice_name=voice.name,
                    voices_bucket=VOICES_BUCKET,
                    save_path=voice_save_path,
                )
            }
        )
        for voice in voices
    ]


def handler(event: dict):
    input_data = WebhookRequest.model_validate(event["input"])
    request = SpeechRequest.model_validate(input_data.data)

    total_word_count = sum(len(segment.text.split()) for segment in request.text)
    data = Response(filename="", request_word_count=total_word_count)
    status = "failed"

    try:
        voices_local = download_voices(request.voices, "/tmp")
        narrated_segments = F5Client(voices=voices_local).generate(request.text)
        upload_narration_segments(
            user_id=request.user_id,
            chapter_name=request.chapter_name,
            segments=narrated_segments,
        )
        segment_audio_paths = download_all_segments(
            user_id=request.user_id,
            chapter_name=request.chapter_name,
        )
        narration_key = build_final_narration(
            user_id=request.user_id,
            chapter_name=request.chapter_name,
            file_paths=segment_audio_paths,
        )

        status = "complete"
        data = Response(filename=narration_key, request_word_count=total_word_count)
    except Exception as e:
        logger.exception("Speech generation failed: %s", str(e))
        status = "failed"
    finally: # TODO: We don't do this in script rp_handler. Refer to our implementation there.
        requests.post(
            url=input_data.callback,
            json=WebhookResponse(
                user_id=input_data.user_id,
                event=input_data.event,
                status=status,
                message="",
                data=data,
            ).model_dump(),
            timeout=120,
        )


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
