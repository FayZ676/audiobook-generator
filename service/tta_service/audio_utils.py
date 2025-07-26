import io
import tempfile
from pathlib import Path
from typing import BinaryIO

from pydub import AudioSegment


def convert_audio_to_mp3(audio_file: BinaryIO) -> io.BytesIO:
    """
    Convert any audio format to MP3.

    Args:
        audio_file: Binary audio file input

    Returns:
        io.BytesIO: MP3 audio data
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_input:
        audio_file.seek(0)
        temp_input.write(audio_file.read())
        temp_input_path = temp_input.name

    try:
        audio = AudioSegment.from_file(temp_input_path)
        mp3_buffer = io.BytesIO()
        audio.export(mp3_buffer, format="mp3", bitrate="128k")
        mp3_buffer.seek(0)

        return mp3_buffer

    finally:
        Path(temp_input_path).unlink(missing_ok=True)


def get_audio_format_from_filename(filename: str) -> str:
    """Get audio format from filename extension."""
    return Path(filename).suffix.lower().lstrip(".")


def is_mp3_format(filename: str) -> bool:
    """Check if file is already MP3 format."""
    return get_audio_format_from_filename(filename) == "mp3"
