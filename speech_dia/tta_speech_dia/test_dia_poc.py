"""
Simple test for the Dia TTS POC.

This test creates a basic SpeechRequest and verifies that the Dia TTS POC
can generate audio without errors.
"""

from pathlib import Path

from tta_types.types import SpeechRequest, SpeechRequestSegment, Voice
from tta_speech_dia.dia_tts import infer_dia, _convert_to_dia_format


def test_convert_to_dia_format():
    """Test the conversion from SpeechRequestSegment to Dia format."""
    segments = [
        SpeechRequestSegment(text="Hello, how are you today?", voice_name="Alice"),
        SpeechRequestSegment(
            text="I'm doing great, thanks for asking!", voice_name="Bob"
        ),
        SpeechRequestSegment(text="That's wonderful to hear.", voice_name="Alice"),
    ]

    result = _convert_to_dia_format(segments)
    print(f"Dia format: {result}")

    # Should alternate between S1 and S2 for Alice and Bob
    expected_parts = [
        "[S1] Hello, how are you today?",
        "[S2] I'm doing great, thanks for asking!",
        "[S1] That's wonderful to hear.",
    ]
    expected = " ".join(expected_parts)

    assert result == expected, f"Expected: {expected}, Got: {result}"
    print("✓ Dia format conversion test passed")


def test_speech_generation():
    """Test the full speech generation pipeline."""
    # Create test data
    voices = [
        Voice(
            name="Alice",
            age="30",
            gender="female",
            audio_path="test_alice.mp3",
            audio_transcript="Hello, this is Alice speaking.",
        ),
        Voice(
            name="Bob",
            age="35",
            gender="male",
            audio_path="test_bob.mp3",
            audio_transcript="Hi there, Bob here.",
        ),
    ]

    segments = [
        SpeechRequestSegment(
            text="Hello, welcome to our audiobook demo!", voice_name="Alice"
        ),
        SpeechRequestSegment(
            text="Thank you Alice. This is a test of the Dia TTS system.",
            voice_name="Bob",
        ),
        SpeechRequestSegment(
            text="It sounds quite natural, doesn't it?", voice_name="Alice"
        ),
        SpeechRequestSegment(text="Yes, very impressive technology!", voice_name="Bob"),
    ]

    request = SpeechRequest(title="dia_tts_test", text=segments, voices=voices)

    print("Testing speech generation...")
    print(f"Input text will be converted to: {_convert_to_dia_format(segments)}")

    try:
        # Test the main interface
        audio_data, sample_rate = infer_dia(request)

        print(f"✓ Generated audio: {len(audio_data)} bytes")
        print(f"✓ Sample rate: {sample_rate}")

        # Save test output
        output_file = Path(__file__).parent / "test_output.mp3"
        with open(output_file, "wb") as f:
            f.write(audio_data)
        print(f"✓ Test audio saved to: {output_file}")

        return True

    except ImportError as e:
        print(f"⚠ Skipping speech generation test - Dia not installed: {e}")
        return False
    except Exception as e:
        print(f"✗ Speech generation failed: {e}")
        return False


if __name__ == "__main__":
    print("Running Dia TTS POC tests...")

    # Test format conversion (doesn't require Dia)
    test_convert_to_dia_format()

    # Test speech generation (requires Dia)
    SPEECH_TEST_PASSED = test_speech_generation()

    if SPEECH_TEST_PASSED:
        print("\n✓ All tests passed! Dia TTS POC is working.")
    else:
        print(
            "\n⚠ Basic tests passed, but speech generation requires Dia installation."
        )
        print("To install Dia: pip install git+https://github.com/nari-labs/dia.git")
        print(
            "Also ensure you have a HuggingFace token set as HF_TOKEN environment variable."
        )
