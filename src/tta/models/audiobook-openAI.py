import os
import openai
from dotenv import load_dotenv

# Function to generate text using OpenAI's chat model
def generate_text(prompt: str) -> str:
    """
    Generate text from the given prompt using OpenAI's GPT model.

    Parameters:
        prompt (str): The input prompt to generate text from.

    Returns:
        str: The generated text from the model.

    Raises:
        RuntimeError: If there is an issue with the OpenAI API call.
    """

    # Replace with your OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')

    try:
        # Call the OpenAI API to get the generated text
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a narrator for an audiobook."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        generated_text = response.choices[0].message['content']
        return generated_text
    
    except Exception as e:
        # Raise the error with more context to help debugging
        raise RuntimeError(f"Failed to generate text from OpenAI API: {e}")
