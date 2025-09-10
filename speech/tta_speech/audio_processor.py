"""Audio processing utilities for speech synthesis."""

from io import BytesIO
from pathlib import Path

from pydub import AudioSegment
from pydub.effects import normalize


class AudioProcessor:
    """Handles audio processing operations like normalization and concatenation."""

    @staticmethod
    def normalize_volume(audio_path: str, headroom: float = 0.1) -> str:
        """Normalize audio volume with specified headroom."""
        try:
            audio = AudioSegment.from_file(audio_path)
            normalized_audio = normalize(audio, headroom=headroom)
            file_format = Path(audio_path).suffix.lstrip(".")
            normalized_audio.export(audio_path, format=file_format)
            return audio_path
        except (FileNotFoundError, ValueError, OSError) as e:
            print(f"Error normalizing audio file {audio_path}: {e}")
            return audio_path

    @staticmethod
    def build_from_segments(audio_segments: list[tuple[bytes, int | None]]) -> bytes:
        """Build a single audio file from multiple segments."""
        combined = AudioSegment.empty()
        for audio_bytes, sample_rate in audio_segments:
            segment = AudioSegment.from_file(
                BytesIO(audio_bytes), format="wav", frame_rate=sample_rate
            )
            combined += segment

        output = BytesIO()
        combined.export(output, format="mp3")
        return output.getvalue()

    @staticmethod
    def concat_from_bytes(audio_data_list: list[bytes]) -> bytes:
        """Concatenate multiple audio byte arrays into a single MP3."""
        combined = AudioSegment.empty()
        for data in audio_data_list:
            segment = AudioSegment.from_file(BytesIO(data), format="mp3")
            combined += segment

        output = BytesIO()
        combined.export(output, format="mp3")
        return output.getvalue()
