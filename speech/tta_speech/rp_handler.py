import os
from io import BytesIO
import logging

import requests
import runpod

from tta_f5.client import F5Client

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    WebhookResponse,
    Response,
)
from tta_aws.s3 import S3Client

from tta_speech.audio_utils import (
    concat_audio_from_files,
    audio_file_to_bytesio,
)
from tta_speech.data_utils import (
    download_audio,
    create_manifest,
    save_manifest_and_narration,
    load_existing_manifest,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")
VOICES_BUCKET = os.environ.get("VOICES_BUCKET", "")


s3 = S3Client()


# TODO: Can this be bundled with the Manifest code? Some sort of TTADataManager class?
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
        voices = download_voices(request.voices, "/tmp")
        result = F5Client(voices=voices).generate(request.text)

        for segment in request.text:
            s3.upload_fileobj(
                bucket_name=PROJECTS_BUCKET,
                file_name=f"{request.user_id}/{request.chapter_name}/audio/segments/{segment.id}.mp3",
                file=audio_file_to_bytesio(result[segment.id]),
            )

        narration_key = f"{request.user_id}/{request.chapter_name}/audio/narration.mp3"
        manifest_key = f"{request.user_id}/{request.chapter_name}/audio/manifest.json"

        existing_manifest = load_existing_manifest(manifest_key, PROJECTS_BUCKET)
        if existing_manifest:
            segment_ids = [s.id for s in existing_manifest.segments]
            ordered_file_paths = [result[seg_id] for seg_id in segment_ids]
            stitched = concat_audio_from_files(ordered_file_paths, audio_format="wav")
            s3.upload_fileobj(PROJECTS_BUCKET, narration_key, BytesIO(stitched))
        else:
            segment_ids = [s.id for s in request.text]
            manifest = create_manifest(
                request.user_id, request.chapter_name, segment_ids, narration_key
            )
            save_manifest_and_narration(
                manifest, manifest_key, narration_key, result, PROJECTS_BUCKET
            )

        status = "complete"
        data = Response(filename=narration_key, request_word_count=total_word_count)
    except Exception as e:
        logger.exception("Speech generation failed: %s", str(e))
        status = "failed"
    finally:
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
