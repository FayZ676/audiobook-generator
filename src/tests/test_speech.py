from tta.models.speech import generate_speech


def test_speech():
    """Test that the function returns bytes."""
    audio_data = generate_speech("Hello", "")
    assert isinstance(audio_data, bytes), "The result should be of type bytes."
