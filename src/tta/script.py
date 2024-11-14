import json
from dataclasses import dataclass
from pydantic import BaseModel
from tta.models.text import generate_text
from tta.character import CharacterVoiced


@dataclass
class Speech:
    speaker: str
    voice_id: str
    text: str


@dataclass
class Script:
    speeches: list[Speech]


class ResponseFormat(BaseModel):
    script: list[Speech]


def parse_response(response: str) -> Script | None:
    try:
        result = json.loads(response)
        speeches = [
            Speech(speaker=s["speaker"], voice_id=s["voice_id"], text=s["text"])
            for s in result["script"]
        ]
        return Script(speeches=speeches)
    except json.JSONDecodeError:
        return None


def convert_text_to_script(
    text: str, characters: list[CharacterVoiced]
) -> Script | None:
    prompt = f"""
    <text>
    {text}
    </text>
    
    <characters>
    {", ".join([f"{character.character.name} ({character.voice.voice_id})" for character in characters])}
    </characters>

    Convert the <text> into a verbatim script where every word is included. Assign all instances of speech to the appropriate character and their voice id specified in <characters>. Assign all other instances of text to the Narrator and give them an empty voice id of "".
    """
    result = generate_text(prompt, ResponseFormat)
    return parse_response(result)
