import unittest
from src.tta.models.elevenlabs import convert_text_to_speech_with_client


class TestTextToSpeech(unittest.TestCase):
    def setUp(self):
        """Set up test variables."""
        self.sample_text = "Hello world!"
        self.voice_id = "pMsXgVXv3BLzUgSXRplE"  # Replace with a known valid voice ID

    def test_convert_text_to_speech_returns_bytes(self):
        """Test that the function returns bytes."""
        audio_data = convert_text_to_speech_with_client(self.sample_text, self.voice_id)
        self.assertIsInstance(audio_data, bytes, "The result should be of type bytes.")

if __name__ == '__main__':
    unittest.main()
