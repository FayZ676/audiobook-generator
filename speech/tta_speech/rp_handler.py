import os
from io import BytesIO
from pathlib import Path

import requests
import runpod
from pydub import AudioSegment
from pydub.effects import normalize

from tta_speech.infer import infer
from tta_speech.inference_types import InferenceParams, InputData

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
    request: list[SpeechRequestSegment], voices: list[Voice], voice_save_path: str
) -> InputData:
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

    text = " ".join([f"[{r.voice_name}] {r.text}" for r in request])
    voices_dict = voices_from_names([r.voice_name for r in request])
    return InputData(text, voices_dict)


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


def _synthesize_segment(segment: SpeechRequestSegment, voices: list[Voice]):
    text_input = _prepare_input([segment], voices, voice_save_path="/tmp")
    return infer(
        InferenceParams(
            gen_text=text_input.text,
            voices=text_input.voices,
            vocab_file=f"{Path(__file__).parent}/vocab.txt",
            vocoder_name="vocos",
            vocoder_local_path=f"{Path(__file__).parent}/vocos",
            load_vocoder_from_local=True,
            remove_silence=True,
            ckpt_file=f"{Path(__file__).parent}/checkpoints/model_1250000.safetensors",
        )
    )


def handler(event: dict):
    request = WebhookRequest.model_validate(event["input"])
    request_data = SpeechRequest.model_validate(request.data)

    total_word_count = sum(len(segment.text.split()) for segment in request_data.text)
    data = Response(filename="", request_word_count=total_word_count)
    status = "failed"

    try:
        segment_results: list[tuple[bytes, int | None]] = []
        for idx, segment in enumerate(request_data.text):
            result = _synthesize_segment(segment, request_data.voices)
            s3.upload_fileobj(
                f"{PROJECTS_BUCKET}",
                f"{request.user_id}/{request_data.chapter_name}/segments/{idx:04d}.mp3",
                BytesIO(_build_audio([result])),
            )
            segment_results.append(result)

        project_narration_path = (
            f"{request.user_id}/{request_data.chapter_name}/narration.mp3"
        )
        s3.upload_fileobj(
            f"{PROJECTS_BUCKET}",
            project_narration_path,
            BytesIO(_build_audio(segment_results)),
        )
        status = "complete"
        data = Response(
            filename=project_narration_path, request_word_count=total_word_count
        )
    except Exception as e:
        # TODO: Instead of raising we should log and set the message, status for the response.
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
