import os

from tta_aws.s3 import S3Client


s3 = S3Client()


def download_audio(
    audio_path: str, voice_name: str, voices_bucket: str, save_path: str
):
    """Download audio file for voice if it itsn't already downloaded."""
    temp_audio_path = f"{save_path}/{voice_name}.wav"
    if not os.path.exists(temp_audio_path):
        audio = S3Client().get_file(voices_bucket, audio_path)
        with open(temp_audio_path, "wb") as f:
            f.write(audio)
    return temp_audio_path
