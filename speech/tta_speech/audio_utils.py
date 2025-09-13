import os
from io import BytesIO
from pathlib import Path

from pydub import AudioSegment
from pydub.effects import normalize

from tta_aws.s3 import S3Client


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")


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
    s3 = S3Client()
    combined = AudioSegment.empty()
    for key in keys:
        data = s3.get_file(PROJECTS_BUCKET, key)
        seg = AudioSegment.from_file(BytesIO(data), format="mp3")
        combined += seg
    out = BytesIO()
    combined.export(out, format="mp3")
    return out.getvalue()