import json
from dataclasses import dataclass
from pydantic import BaseModel
from tta.models.text import generate_text


@dataclass
class Speech:
    speaker: str
    text: str


@dataclass
class Script:
    speeches: list[Speech]


class ResponseFormat(BaseModel):
    script: list[Speech]


def parse_response(response: str) -> Script:
    try:
        result = json.loads(response)
        speeches = [
            Speech(speaker=s["speaker"], text=s["text"]) for s in result["script"]
        ]
        return Script(speeches=speeches)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to decode JSON response: {e}") from e


def convert_text_to_script(text: str) -> Script:
    prompt = f"""
    Convert the following text into a structured script. Include both the parts spoken by characters and the narrator:
    {text}
    """
    result = generate_text(prompt, ResponseFormat)
    return parse_response(result)
