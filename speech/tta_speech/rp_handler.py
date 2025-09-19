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
from tta_data.client import TTADataClient

from tta_speech.audio_utils import concat_audio_from_files


def handler(event: dict):
    input_data = WebhookRequest.model_validate(event["input"])
    request = SpeechRequest.model_validate(input_data.data)

    total_word_count = sum(len(segment.text.split()) for segment in request.text)
    data = Response(filename="", request_word_count=total_word_count)
    status = "failed"

    data_client = TTADataClient()

    try:
        voices = _download_voices(
            data_client=data_client, voices=request.voices, voice_save_path="/tmp"
        )
        result = F5Client(voices=voices).generate(segments=request.text)

        for segment in request.text:
            data_client.upload_speech(
                user_id=request.user_id,
                chapter_name=request.chapter_name,
                speech_file_path=result[segment.id],
            )

        existing_manifest = data_client.get_speech_manifest(
            user_id=request.user_id, chapter_name=request.chapter_name
        )

        # NOTE: This whole manifest section doesn't make much sense to me.
        if existing_manifest:
            segment_ids = [s.id for s in existing_manifest.segments]
            file_paths = [result[seg_id] for seg_id in segment_ids]
        else:
            segment_ids = [s.id for s in request.text]
            file_paths = [result[seg_id] for seg_id in segment_ids]
            data_client.upload_speech_manifest(
                user_id=request.user_id,
                chapter_name=request.chapter_name,
                segment_ids=segment_ids,
            )

        stitched_path = concat_audio_from_files(file_paths=file_paths)
        narration_path = data_client.upload_speech(
            user_id=request.user_id,
            chapter_name=request.chapter_name,
            speech_file_path=stitched_path,
        )
        status = "complete"
        data = Response(filename=narration_path, request_word_count=total_word_count)
    except Exception as e:
        raise e from e
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


def _download_voices(
    data_client: TTADataClient, voices: list[Voice], voice_save_path: str
) -> list[Voice]:
    return [
        voice.model_copy(
            update={
                "audio_path": data_client.get_voice(
                    voice_audio_file_path=voice.audio_path,
                    voice_name=voice.name,
                    save_path=voice_save_path,
                )
            }
        )
        for voice in voices
    ]


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
