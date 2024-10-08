import json
from dataclasses import dataclass
from typing import List
from pydantic import BaseModel
from tta.models.text import generate_text

@dataclass
class Speech:
    speaker: str
    text: str

@dataclass
class Script:
    speeches: List[Speech]

# Define a response format that matches your Script structure
class ResponseFormat(BaseModel):
    script: List[Speech]

def parse_response(response: str) -> Script:
    try:
        # Convert the response string to JSON and then parse it into Script format
        result = json.loads(response)
        speeches = [Speech(speaker=s["speaker"], text=s["text"]) for s in result["script"]]
        return Script(speeches=speeches)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to decode JSON response: {e}")

def convert_text_to_script(text: str) -> Script:
    # Create a prompt for OpenAI to convert text into a structured script
    prompt = f"""
    Convert the following text into a structured script. Include both the parts spoken by characters and the narrator:
    {text}
    """
    # Use generate_text to get structured output
    result = generate_text(prompt, ResponseFormat)

    # Parse the result into a Script using the parsing function
    return parse_response(result)