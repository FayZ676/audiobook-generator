from tta.models.speech import generate_speech


def test_speech__returns_bytes():
    """Test that the function returns bytes."""
    audio_data = generate_speech("Hello", "5ZvI0fBo2w7CxuiM9ObF")
    assert isinstance(audio_data, bytes), "The result should be of type bytes."
