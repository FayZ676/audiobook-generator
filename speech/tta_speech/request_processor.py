"""Request processing orchestrator for speech synthesis."""

from typing import Dict

from tta_speech.voice_manager import VoiceManager
from tta_speech.speech_synthesizer import SpeechSynthesizer
from tta_speech.storage_manager import StorageManager
from tta_speech.text_utils import compute_word_count

from tta_types.types import SpeechRequest, Response


class SpeechRequestProcessor:
    """Orchestrates the processing of speech synthesis requests."""

    def __init__(
        self,
        voice_manager: VoiceManager,
        speech_synthesizer: SpeechSynthesizer,
        storage_manager: StorageManager,
    ):
        self.voice_manager = voice_manager
        self.speech_synthesizer = speech_synthesizer
        self.storage_manager = storage_manager

    def process_request(self, request_data: SpeechRequest, user_id: str) -> Response:
        """Process a complete speech synthesis request."""
        segment_audio_data: Dict[str, bytes] = {}
        for segment in request_data.text:
            voice = self.voice_manager.get_voice_by_name(
                voices=request_data.voices, voice_name=segment.voice_name
            )
            audio_data = self.speech_synthesizer.synthesize_segment(segment, voice)
            segment_audio_data[segment.id] = audio_data
            self.storage_manager.upload_segment_audio(
                user_id=user_id,
                chapter_name=request_data.chapter_name,
                segment_id=segment.id,
                audio_data=audio_data,
            )

        narration_key = self._create_final_narration(
            request_data=request_data,
            user_id=user_id,
            segment_audio_data=segment_audio_data,
        )

        return Response(
            filename=narration_key,
            request_word_count=compute_word_count(request_data.text),
        )

    def _create_final_narration(
        self,
        request_data: SpeechRequest,
        user_id: str,
        segment_audio_data: Dict[str, bytes],
    ) -> str:
        """Create the final narration file from segments."""
        manifest = self.storage_manager.get_manifest(user_id, request_data.chapter_name)

        if manifest:
            segment_keys = [s.get("key") for s in manifest.get("segments", [])]
            audio_files = self.storage_manager.get_audio_files(segment_keys)
            stitched_audio = self.speech_synthesizer.create_narration_from_segments(
                audio_files
            )
        else:
            if len(request_data.text) > 1:
                ordered_ids = [s.id for s in request_data.text]
                ordered_audio = [segment_audio_data[seg_id] for seg_id in ordered_ids]
                stitched_audio = self.speech_synthesizer.create_narration_from_segments(
                    ordered_audio
                )
                manifest_data = self.storage_manager.create_manifest_data(
                    user_id=user_id,
                    chapter_name=request_data.chapter_name,
                    segment_ids=ordered_ids,
                )
                self.storage_manager.upload_manifest(
                    user_id=user_id,
                    chapter_name=request_data.chapter_name,
                    manifest_data=manifest_data,
                )
            else:
                stitched_audio = next(iter(segment_audio_data.values()))

        return self.storage_manager.upload_narration_audio(
            user_id=user_id,
            chapter_name=request_data.chapter_name,
            audio_data=stitched_audio,
        )
