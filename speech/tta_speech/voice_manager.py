"""Voice management for speech synthesis."""

import os
from pathlib import Path
from typing import Dict

from tta_types.types import Voice
from tta_aws.s3 import S3Client


class VoiceManager:
    """Manages voice assets including downloading and caching."""

    def __init__(self, s3_client: S3Client, voices_bucket: str):
        self.s3_client = s3_client
        self.voices_bucket = voices_bucket
        self._voice_cache: Dict[str, str] = {}  # voice_name -> local_path

    def get_voice_by_name(self, voices: list[Voice], voice_name: str) -> Voice:
        """Find a voice by name from the available voices."""
        try:
            return next(voice for voice in voices if voice.name == voice_name)
        except StopIteration as exc:
            raise ValueError(
                f"Voice '{voice_name}' not found in available voices"
            ) from exc

    def download_voice_audio(self, voice: Voice, save_directory: str) -> str:
        """Download voice audio file if not already cached."""
        cache_key = f"{voice.name}_{voice.audio_path}"
        if cache_key in self._voice_cache:
            return self._voice_cache[cache_key]

        Path(save_directory).mkdir(parents=True, exist_ok=True)
        audio_data = self.s3_client.get_file(self.voices_bucket, voice.audio_path)
        filename = voice.audio_path.split("/")[-1]
        local_path = os.path.join(save_directory, filename)

        with open(local_path, "wb") as f:
            f.write(audio_data)

        self._voice_cache[cache_key] = local_path
        return local_path

    def prepare_voice_dict(self, voice: Voice, audio_path: str) -> dict:
        """Prepare voice dictionary for inference."""
        return {
            "ref_audio": audio_path,
            "ref_text": voice.audio_transcript,
        }
