from tta.models.text_to_speech import generate_text


def test_generate_text():
    result = generate_text("Say 'Hello'")
    assert isinstance(result, str)
