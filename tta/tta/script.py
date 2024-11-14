import json
from string import Template
from dataclasses import dataclass
from pydantic import BaseModel
from tta.models.text import generate_text
from tta.character import CharacterVoiced


@dataclass
class Speech:
    speaker: str
    voice_id: str
    text: str


class ResponseFormat(BaseModel):
    script: list[Speech]


def parse_response(response: str) -> list[Speech]:
    result = json.loads(response)
    speeches = [
        Speech(
            speaker=s["speaker"],
            voice_id=str(s["voice_id"]).strip(),
            text=str(s["text"]).strip(),
        )
        for s in result["script"]
    ]
    return speeches


def convert_text_to_script(
    text: str, characters: list[CharacterVoiced]
) -> list[Speech]:
    prompt = Template(
        """
<text>
$text
</text>

<characters>
$characters
</characters>

Split the <text> into parts that should be read by a character and parts that should be read by the Narrator.
Only assign text to a character that they explicitly speak. Assign all other text to the Narrator. 

For example, in the text "'Hello' said Tom" the response should be:
[
    {
        "text": "Hello",
        "voice_id": "123",
        "speaker": "Tom",
    },
    {
        "text": "said Tom.",
        "voice_id": "456",
        "speaker": "Narrator",
    }
]
"""
    ).substitute(
        text=text,
        characters=", ".join(
            [
                f"{character.character.name} ({character.voice.voice_id})"
                for character in characters
            ]
        ),
    )
    result = generate_text(prompt, ResponseFormat)
    return parse_response(result)
