import os
from io import BytesIO
import json

import requests
import runpod

from tta_f5.infer import infer
from tta_f5.inference_types import InferenceParams, InputData

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    SpeechRequestSegment,
    WebhookResponse,
    Response,
)
from tta_aws.s3 import S3Client
from tta_speech.audio_utils import build_audio, concat_mp3_from_keys


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")
VOICES_BUCKET = os.environ.get("VOICES_BUCKET", "")


s3 = S3Client()


def _prepare_input(
    request: list[SpeechRequestSegment], voices: list[Voice], voice_save_path: str
) -> InputData:
    def download_audio(audio_path: str, voice_name: str):
        """Download audio file for voice if it itsn't already downloaded."""
        temp_audio_path = f"{voice_save_path}/{voice_name}.wav"
        if not os.path.exists(temp_audio_path):
            audio = s3.get_file(VOICES_BUCKET, audio_path)
            with open(temp_audio_path, "wb") as f:
                f.write(audio)
        return temp_audio_path

    def voice_to_dict(path, transcript):
        return {
            "ref_audio": path,
            "ref_text": transcript,
        }

    def voices_from_names(voice_names: list[str]):
        return {
            voice.name: voice_to_dict(
                path=download_audio(voice.audio_path, voice.name),
                transcript=voice.audio_transcript,
            )
            for voice in voices
            if voice.name in voice_names
        }

    text = " ".join([f"[{r.voice_name}] {r.text}" for r in request])
    voices_dict = voices_from_names([r.voice_name for r in request])
    return InputData(text, voices_dict)


def _synthesize_segment(segment: SpeechRequestSegment, voices: list[Voice]):
    text_input = _prepare_input([segment], voices, voice_save_path="/tmp")
    return infer(
        InferenceParams(
            gen_text=text_input.text,
            voices=text_input.voices,
            load_vocoder_from_local=True,
            remove_silence=False,
        )
    )


# TODO: This is doing way too much. Needs simplification.
def handler(event: dict):
    request = WebhookRequest.model_validate(event["input"])
    request_data = SpeechRequest.model_validate(request.data)

    total_word_count = sum(len(segment.text.split()) for segment in request_data.text)
    data = Response(filename="", request_word_count=total_word_count)
    status = "failed"

    try:
        segment_results: dict[str, tuple[bytes, int | None]] = {}
        for segment in request_data.text:
            segment_results[segment.id] = _synthesize_segment(
                segment, request_data.voices
            )
            segment_key = f"{request.user_id}/{request_data.chapter_name}/audio/segments/{segment.id}.mp3"
            s3.upload_fileobj(
                PROJECTS_BUCKET,
                segment_key,
                BytesIO(build_audio([segment_results[segment.id]])),
            )

        narration_key = (
            f"{request.user_id}/{request_data.chapter_name}/audio/narration.mp3"
        )
        manifest_key = (
            f"{request.user_id}/{request_data.chapter_name}/audio/manifest.json"
        )

        manifest_exists = bool(s3.list_files(PROJECTS_BUCKET, manifest_key))
        if manifest_exists:
            manifest = json.loads(
                s3.get_file(PROJECTS_BUCKET, manifest_key).decode("utf-8")
            )
            segment_keys_in_order = [s.get("key") for s in manifest.get("segments", [])]
            stitched = concat_mp3_from_keys(segment_keys_in_order)
            s3.upload_fileobj(f"{PROJECTS_BUCKET}", narration_key, BytesIO(stitched))
            status = "complete"
            data = Response(filename=narration_key, request_word_count=total_word_count)
        else:
            if len(request_data.text) > 1:
                ordered_ids = [s.id for s in request_data.text]
                manifest_segments = [
                    {
                        "id": seg_id,
                        "index": idx,
                        "key": f"{request.user_id}/{request_data.chapter_name}/audio/segments/{seg_id}.mp3",
                    }
                    for idx, seg_id in enumerate(ordered_ids)
                ]
                stitched = concat_mp3_from_keys([m["key"] for m in manifest_segments])
                s3.upload_fileobj(
                    f"{PROJECTS_BUCKET}", narration_key, BytesIO(stitched)
                )
                manifest = {
                    "narration": {"key": narration_key},
                    "segments": manifest_segments,
                }
                s3.upload_fileobj(
                    f"{PROJECTS_BUCKET}",
                    manifest_key,
                    BytesIO(json.dumps(manifest).encode("utf-8")),
                )
                status = "complete"
                data = Response(
                    filename=narration_key, request_word_count=total_word_count
                )
            else:
                only = next(iter(segment_results.values()))
                s3.upload_fileobj(
                    f"{PROJECTS_BUCKET}", narration_key, BytesIO(build_audio([only]))
                )
                status = "complete"
                data = Response(
                    filename=narration_key, request_word_count=total_word_count
                )
    except Exception as e:
        raise e from e
    finally:
        requests.post(
            url=request.callback,
            json=WebhookResponse(
                user_id=request.user_id,
                event=request.event,
                status=status,
                message="",
                data=data,
            ).model_dump(),
            timeout=120,
        )


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
