import os
from io import BytesIO
from pathlib import Path
import json

import requests
import runpod
from pydub import AudioSegment
from pydub.effects import normalize

from tta_speech.infer import DiaTTS

from tta_types.types import (
    Voice,
    WebhookRequest,
    SpeechRequest,
    SpeechRequestSegment,
    WebhookResponse,
    Response,
)
from tta_aws.s3 import S3Client


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")
VOICES_BUCKET = os.environ.get("VOICES_BUCKET", "")


s3 = S3Client()


def normalize_audio_volume(audio_path: str, headroom: float = 0.1) -> str:
    try:
        audio = AudioSegment.from_file(audio_path)
        normalized_audio = normalize(audio, headroom=headroom)
        file_format = Path(audio_path).suffix.lstrip(".")
        normalized_audio.export(audio_path, format=file_format)
        return audio_path
    except Exception as e:
        print(f"Error normalizing audio file {audio_path}: {e}")
        return audio_path


# NOTE: I hate that we need to download the audio.
def _prepare_input(
    request: SpeechRequestSegment, voice: Voice, voice_save_path: str
) -> str:
    def download_audio(audio_path: str):
        audio = s3.get_file(VOICES_BUCKET, audio_path)
        temp_audio_path = f"{voice_save_path}/{audio_path.split('/')[-1]}"
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
                path=download_audio(voice.audio_path),
                transcript=voice.audio_transcript,
            )
            for voice in voices
            if voice.name in voice_names
        }

    # TODO: Complete
    return ""


def _build_audio(audio_segments: list[tuple[bytes, int | None]]) -> bytes:
    combined = AudioSegment.empty()
    for audio_bytes, sample_rate in audio_segments:
        segment = AudioSegment.from_file(
            BytesIO(audio_bytes), format="wav", frame_rate=sample_rate
        )
        combined += segment

    output = BytesIO()
    combined.export(output, format="mp3")
    return output.getvalue()


def _concat_mp3_from_keys(keys: list[str]) -> bytes:
    combined = AudioSegment.empty()
    for key in keys:
        data = s3.get_file(PROJECTS_BUCKET, key)
        seg = AudioSegment.from_file(BytesIO(data), format="mp3")
        combined += seg
    out = BytesIO()
    combined.export(out, format="mp3")
    return out.getvalue()


def _synthesize_segment(
    segment: SpeechRequestSegment, voice: Voice
) -> tuple[bytes, int | None]:
    # TODO: Preprocess the text to be in the format dia needs for inference.
    text = segment.text
    # TODO: Fetch and download the voice audio using the voice.audio_path. Don't download if already downloaded.
    audio_path = voice.audio_path
    DiaTTS().generate(
        text=text,
        reference_audio_path=audio_path,
        reference_audio_transcript=voice.audio_transcript,
        output_path="",  # TODO: Where should we save?
    )
    # TODO: We need to return the audio in this format. Or do we?
    return (b"", 0)


def get_voice_for_name(voices: list[Voice], voice_name: str):
    return next(voice for voice in voices if voice.name == voice_name)


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
                segment=segment,
                voice=get_voice_for_name(
                    voices=request_data.voices, voice_name=segment.voice_name
                ),
            )
            s3.upload_fileobj(
                PROJECTS_BUCKET,
                f"{request.user_id}/{request_data.chapter_name}/audio/segments/{segment.id}.mp3",
                BytesIO(_build_audio([segment_results[segment.id]])),
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
            stitched = _concat_mp3_from_keys(segment_keys_in_order)
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
                stitched = _concat_mp3_from_keys([m["key"] for m in manifest_segments])
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
                    f"{PROJECTS_BUCKET}", narration_key, BytesIO(_build_audio([only]))
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
