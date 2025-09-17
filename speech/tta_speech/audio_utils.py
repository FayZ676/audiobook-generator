import os
from io import BytesIO

from pydub import AudioSegment


PROJECTS_BUCKET = os.environ.get("PROJECTS_BUCKET", "")


def audio_file_to_bytesio(file_path: str) -> BytesIO:
    with open(file_path, "rb") as audio_file:
        audio_data = audio_file.read()
    return BytesIO(audio_data)


def concat_audio_from_files(file_paths: list[str], audio_format: str) -> bytes:
    """Concatenate MP3 files from local file paths."""
    combined = AudioSegment.empty()
    for file_path in file_paths:
        seg = AudioSegment.from_file(file_path, format=audio_format)
        combined += seg
    out = BytesIO()
    combined.export(out, format="mp3")
    return out.getvalue()
