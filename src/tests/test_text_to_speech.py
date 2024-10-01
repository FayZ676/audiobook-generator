import json

from pydantic import BaseModel

from tta.models.text_to_speech import generate_text


def test_generate_text():
    class Greeting(BaseModel):
        greeting: str

    result = generate_text("Say 'Hello'", Greeting)
    assert isinstance(json.loads(result)["greeting"], str)
