#!/usr/bin/env python3
"""
Example usage of the Dia TTS POC.

This script demonstrates how to use the Dia TTS POC to generate speech
from a SpeechRequest, similar to how the existing F5-TTS system works.
"""

from tta_types.types import SpeechRequest, SpeechRequestSegment, Voice
from tta_speech_dia.dia_tts import infer_dia


def main():
    """Main example function."""
    print("Dia TTS POC Example")
    print("=" * 20)

    voices = [
        Voice(
            name="Narrator",
            age="40",
            gender="neutral",
            audio_path="voices/narrator.mp3",
            audio_transcript="Welcome to our story.",
        ),
        Voice(
            name="Character1",
            age="25",
            gender="female",
            audio_path="voices/char1.mp3",
            audio_transcript="Hello there!",
        ),
        Voice(
            name="Character2",
            age="30",
            gender="male",
            audio_path="voices/char2.mp3",
            audio_transcript="How are you doing?",
        ),
    ]

    segments = [
        SpeechRequestSegment(
            text="Once upon a time, in a land far away, there lived two friends.",
            voice_name="Narrator",
        ),
        SpeechRequestSegment(
            text="Good morning! What a beautiful day it is today.",
            voice_name="Character1",
        ),
        SpeechRequestSegment(
            text="Indeed it is! Perfect weather for an adventure.",
            voice_name="Character2",
        ),
    ]

    request = SpeechRequest(title="example_dialogue", text=segments, voices=voices)

    audio_data, sample_rate = infer_dia(request)

    output_file = "example_output.mp3"
    with open(output_file, "wb") as f:
        f.write(audio_data)


if __name__ == "__main__":
    main()
