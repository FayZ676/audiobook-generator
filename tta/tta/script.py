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
    prompt = PROMPT.substitute(
        text=text,
        characters=", ".join(
            [
                f"{character.character.name} ({character.voice.voice_id})"
                for character in characters
            ]
        ),
    )
    result = generate_text(str(SYS_PROMPT), prompt, ResponseFormat)
    return parse_response(result)


SYS_PROMPT = """
Split a book's text into dialogue segments, categorizing each chunk as either narration or character dialogue, while preserving the original content. A list of character names corresponding with individuals in the text will be provided. Use it to attribute the text to the appropriate character accordingly.

Ensure each segment is properly attributed, capturing who is speaking and differentiating when the narrator is providing descriptive context versus when characters are engaging in dialogue. Maintain all detailed content from the source throughout the segmentation process.

# Steps

1. **Identify Dialogue and Narration**:
    - Distinguish between dialogue by characters and descriptive passages by the narrator.
    - Identify textual indicators like quotation marks for spoken dialogue and absence of these for narration.

2. **Utilize Provided Name List**:
    - Refer to the list of character names given to accurately attribute dialogue.
    - Use context clues when the speaker is ambiguous to select from the provided list.

3. **Attribute Segments**:
    - Assign each segment as either "Narrator" or associate it with the respective character speaking.
    - Extract the character names clearly and ensure that the text for each character's speech maintains its integrity.

4. **Create Segments**:
    - Split the text into understandable chunks, categorizing them in sequence.
    - Each segment should be structured to clearly denote whether it involves the narrator or a specific character's dialogue.

# Notes

- Ensure the segmentation respects punctuation and the logical flow of the story.
- Use the provided character name list to accurately attribute dialogue. If a character's name isn't explicitly mentioned, cross-check the context with the list of names.
- Maintain chronology and readability of the original narrative to ensure no confusion arises between character dialogue and narration.
- Ensure to verify ambiguous dialogue by matching context with the names provided.
"""

PROMPT = Template(
    """
<characters>
$characters
</characters>
    
<text>
$text
</text>
"""
)
