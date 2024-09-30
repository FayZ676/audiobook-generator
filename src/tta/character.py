import sys
import os
import json
from dataclasses import dataclass
from typing import List, Literal
from dotenv import load_dotenv

load_dotenv()

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.models.text_to_speech import generate_text

@dataclass
class Character:
    name: str
    age: Literal['child', 'young adult', 'middle-aged', 'elderly']
    gender: Literal['male', 'female']

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

# Example paragraph
text = """
Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview. Our clients were punctual to their appointment, for the clock had just struck ten when Dr. Mortimer was shown up, followed by the young baronet. The latter was a small, alert, dark-eyed man about thirty years of age, very sturdily built, with thick black eyebrows and a strong, pugnacious face. He wore a ruddy-tinted tweed suit and had the weather-beaten appearance of one who has spent most of his time in the open air, and yet there was something in his steady eye and the quiet assurance of his bearing which indicated the gentleman.

“This is Sir Henry Baskerville,” said Dr. Mortimer.

“Why, yes,” said he, “and the strange thing is, Mr. Sherlock Holmes, that if my friend here had not proposed coming round to you this morning I should have come on my own account. I understand that you think out little puzzles, and I’ve had one this morning which wants more thinking out than I am able to give it.”

“Pray take a seat, Sir Henry. Do I understand you to say that you have yourself had some remarkable experience since you arrived in London?”

“Nothing of much importance, Mr. Holmes. Only a joke, as like as not. It was this letter, if you can call it a letter, which reached me this morning.”
"""

# Identify characters
characters_info = identify_characters(text)

# Save the output to memory
character_info_memory = characters_info
