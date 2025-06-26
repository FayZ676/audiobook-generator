"""
Dia TTS POC implementation for audiobook generation.

This module provides a simple interface that matches the existing speech generation
system but uses the Dia TTS model from nari-labs instead of F5-TTS.
"""

import os
import platform
import tempfile
from typing import Optional

from dia.model import Dia

from tta_types.types import SpeechRequest, SpeechRequestSegment


def generate_speech(request: SpeechRequest) -> bytes:
    """
    Generate speech audio from a SpeechRequest using Dia TTS.

    Args:
        request: SpeechRequest containing title, text segments with voice names, and voice definitions

    Returns:
        bytes: MP3 audio data
    """

    dia_text = _convert_to_dia_format(request.text)

    try:
        model = Dia.from_pretrained("nari-labs/Dia-1.6B", compute_dtype="float16")
    except Exception as e:
        raise RuntimeError(f"Failed to load Dia model: {e}") from e

    try:
        is_mac = platform.system() == "Darwin"
        use_compile = not is_mac

        output = model.generate(dia_text, use_torch_compile=use_compile, verbose=True)
    except Exception as e:
        raise RuntimeError(f"Failed to generate speech: {e}") from e

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            model.save_audio(temp_file.name, output)
            temp_file.flush()

            with open(temp_file.name, "rb") as f:
                audio_data = f.read()

            os.unlink(temp_file.name)

            return audio_data

    except Exception as e:
        raise RuntimeError(f"Failed to save audio: {e}") from e


def _convert_to_dia_format(text_segments: list[SpeechRequestSegment]) -> str:
    """
    Convert SpeechRequestSegment list to Dia's speaker format.

    Dia uses [S1] and [S2] speaker tags for dialogue. We'll map different
    voice names to alternating speakers.

    Args:
        text_segments: List of text segments with voice names

    Returns:
        str: Formatted text for Dia TTS
    """
    if not text_segments:
        return ""

    unique_voices = []
    seen = set()
    for segment in text_segments:
        if segment.voice_name not in seen:
            unique_voices.append(segment.voice_name)
            seen.add(segment.voice_name)

    voice_to_speaker = {}
    for i, voice in enumerate(unique_voices):
        voice_to_speaker[voice] = f"S{(i % 2) + 1}"

    dia_parts = []
    for segment in text_segments:
        speaker = voice_to_speaker[segment.voice_name]
        dia_parts.append(f"[{speaker}] {segment.text}")

    return " ".join(dia_parts)


def infer_dia(request: SpeechRequest) -> tuple[bytes, Optional[int]]:
    """
    Inference function that matches the existing TTS interface.

    Args:
        request: SpeechRequest with text and voice data

    Returns:
        tuple[bytes, Optional[int]]: Audio bytes and sample rate (None for MP3)
    """
    audio_data = generate_speech(request)
    return audio_data, None
