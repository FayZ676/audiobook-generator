"""Speech synthesis core functionality."""

import tempfile
from pathlib import Path

from tta_speech.infer import DiaTTS
from tta_speech.voice_manager import VoiceManager
from tta_speech.audio_processor import AudioProcessor
from tta_types.types import Voice, SpeechRequestSegment


class SpeechSynthesizer:
    """Handles speech synthesis operations."""

    def __init__(self, voice_manager: VoiceManager):
        self.voice_manager = voice_manager
        self.audio_processor = AudioProcessor()
        self._tts_model = None

    @property
    def tts_model(self) -> DiaTTS:
        """Lazy load TTS model to avoid initialization overhead."""
        if self._tts_model is None:
            self._tts_model = DiaTTS()
        return self._tts_model

    def synthesize_segment(self, segment: SpeechRequestSegment, voice: Voice) -> bytes:
        """Synthesize a single text segment using the specified voice."""
        with tempfile.TemporaryDirectory() as temp_dir:
            voice_audio_path = self.voice_manager.download_voice_audio(voice, temp_dir)
            output_path = Path(temp_dir) / f"output_{segment.id}.wav"
            self.tts_model.generate(
                text=segment.text,
                reference_audio_path=voice_audio_path,
                reference_audio_transcript=voice.audio_transcript,
                output_path=str(output_path),
            )

            with open(output_path, "rb") as f:
                wav_data = f.read()

            return self.audio_processor.build_from_segments([(wav_data, None)])

    def create_narration_from_segments(self, segment_audio_data: list[bytes]) -> bytes:
        """Create a complete narration by concatenating segment audio data."""
        return self.audio_processor.concat_from_bytes(segment_audio_data)
