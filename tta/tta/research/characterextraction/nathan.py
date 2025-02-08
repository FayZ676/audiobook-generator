import json

from pydantic import BaseModel

from tta.models.text import generate_text
from tta.ner import extract_entities


class ResponseFormat(BaseModel):
    response: list[str]


def build_prompt(entities_list, text):
    prompt = f"""
    <text>
    {text}
    </text>

    <names>
    {entities_list}
    </names>

    The <names> are just suggestions and not necessarily true.
    We are looking specifically for the names of characters that are speakers, i.e., they say something in the text, typically with quotation marks.
    Please combine names that refer to the same character and identify them as one character using the most commonly used name, for example if a character is referred to by their first and last name, or just their first or last name, identify them as by the name used most often, keep a count of name occurances to help identify the main name of each character. 
    
    Do not include any preamble or postamble text in your response.
    Respond only with a list of names, For example:
    ["Name1", "Name2", "Name3"]
    """
    return prompt


def main(text: str) -> set[str]:
    entities = extract_entities(text, ["PERSON"])
    result = generate_text(
        "", build_prompt(entities, text), response_format=ResponseFormat
    )
    return {name for name in json.loads(result)["response"]}
