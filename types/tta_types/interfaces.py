from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from tta_types.types import SpeechRequestSegment, Voice


SegmentId = str
SpeechAudioPath = str
VoiceName = str
PreparedVoiceType = TypeVar("PreparedVoiceType")
SpeechResult = TypeVar("SpeechResult")


class SpeechGeneratorInterface(ABC, Generic[PreparedVoiceType, SpeechResult]):
    def __init__(self, voices: list[Voice]):
        pass

    @abstractmethod
    def generate(
        self, segments: list[SpeechRequestSegment]
    ) -> dict[SegmentId, SpeechAudioPath]:
        """Generate speech for each segment, returning the paths of the processed segments."""

    @staticmethod
    @abstractmethod
    def _prepare_voices(voices: list[Voice]) -> dict[VoiceName, PreparedVoiceType]:
        """Prepare voices for speech generation."""

    @staticmethod
    @abstractmethod
    def _save_result(result: SpeechResult, sample_rate: int) -> str:
        """Save result to /tmp directory for consumption"""
