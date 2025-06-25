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
            audio_path="narrator.mp3",
            audio_transcript="Welcome to our story.",
        ),
        Voice(
            name="Character1",
            age="25",
            gender="female",
            audio_path="char1.mp3",
            audio_transcript="Hello there!",
        ),
        Voice(
            name="Character2",
            age="30",
            gender="male",
            audio_path="char2.mp3",
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

    print(f"Processing {len(segments)} text segments with {len(voices)} voices...")
    print(f"Total characters: {sum(len(s.text) for s in segments)}")

    try:
        audio_data, sample_rate = infer_dia(request)

        print(f"\n✓ Successfully generated audio!")
        print(f"  Audio size: {len(audio_data):,} bytes")
        print(f"  Sample rate: {sample_rate}")

        output_file = "example_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_data)

        print(f"  Saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error generating audio: {e}")


if __name__ == "__main__":
    main()
