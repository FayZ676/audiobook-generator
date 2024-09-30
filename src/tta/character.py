import json
from dataclasses import dataclass
from typing import List, Literal
from dotenv import load_dotenv

from tta.models.text_to_speech import generate_text


load_dotenv()


@dataclass
class Character:
    name: str
    age: Literal["child", "young adult", "middle-aged", "elderly"]
    gender: Literal["male", "female"]


def identify_characters(text: str) -> List[Character]:
    prompt = f"""
    Analyze the following paragraph and identify the speaking characters, their age (categorized as child, young adult, middle-aged, or elderly), and gender:
    
    {text}
    
    Provide the information in the format: 
    [
        {{ "name": "Character Name", "age": "child/young adult/middle-aged/elderly", "gender": "male/female" }},
        ...
    ]
    """

    result = generate_text(prompt)
    print("Generated Text Result:", result)  # Debugging line to check the output

    try:
        characters = json.loads(result)
        return [Character(**char) for char in characters]
    except json.JSONDecodeError as e:
        print("JSONDecodeError:", e)
        return []
