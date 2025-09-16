from pathlib import Path

from tta_types.types import Voice, SpeechRequestSegment

from tta_f5.client import F5Client


def test_infer():
    """Test the infer function by generating audio with faizi_standard voice."""

    test_data_dir = Path(__file__).parent / "data"
    result = F5Client(
        voices=[
            Voice(
                name="faizi_standard",
                age="middle-aged",
                gender="male",
                audio_path=str(test_data_dir / "faizi_standard.mp3"),
                audio_transcript="I chase the quiet stories—rooftop gardens at dawn, old songs on street corners. Every question is a doorway to something deeper.",
            )
        ]
    ).generate(
        segments=[
            SpeechRequestSegment(
                id="seg-000",
                text="Hello, this is a test of the text-to-speech system.",
                voice_name="faizi_standard",
            ),
            SpeechRequestSegment(
                id="seg-000",
                text="Can you hear me?.",
                voice_name="faizi_standard",
            ),
        ]
    )
    print(f"RESULTS SAVED TO {result}")


if __name__ == "__main__":
    test_infer()
