import os
import openai
from dotenv import load_dotenv

# Load environment variables (for the OpenAI API key)
load_dotenv()

# Initialize OpenAI API client with the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script_from_text(book_text: str) -> str:
    """
    Convert the book text into a structured script format with dialogues and speaker names using OpenAI's Functions API.
    """
    try:
        # Send the book text to OpenAI API and force structured output via the Functions API
        response = openai.ChatCompletion.create(
            model="gpt-4-0613", 
            messages=[
                {
                    "role": "user",
                    "content": f"Convert this book text into a structured script format: {book_text}"
                }
            ],
            functions=[
                {
                    "name": "generate_script",
                    "description": "Generates a script from book text with dialogues and speaker names",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "script": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "speaker": {"type": "string"},
                                    },
                                    "required": ["text", "speaker"]
                                }
                            }
                        },
                        "required": ["script"]
                    }
                }
            ],
            function_call={"name": "generate_script"}  # Force the function to be invoked
        )
        
        # Extract the structured script data from the API response
        script_data = response.choices[0].message['function_call']['arguments']
        
        return script_data 

    except Exception as e:
        raise RuntimeError(f"Failed to generate structured script from OpenAI API: {e}") from e
