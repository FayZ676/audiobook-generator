import os
from io import BytesIO

from pydub import AudioSegment

from tta_aws.s3 import S3Client


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")


def build_audio(audio_segments: list[tuple[bytes, int | None]]) -> bytes:
    combined = AudioSegment.empty()
    for audio_bytes, sample_rate in audio_segments:
        segment = AudioSegment.from_file(
            BytesIO(audio_bytes), format="wav", frame_rate=sample_rate
        )
        combined += segment

    output = BytesIO()
    combined.export(output, format="mp3")
    return output.getvalue()


def concat_mp3_from_keys(keys: list[str]) -> bytes:
    s3 = S3Client()
    combined = AudioSegment.empty()
    for key in keys:
        data = s3.get_file(PROJECTS_BUCKET, key)
        seg = AudioSegment.from_file(BytesIO(data), format="mp3")
        combined += seg
    out = BytesIO()
    combined.export(out, format="mp3")
    return out.getvalue()
