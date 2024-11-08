import os

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text(prompt: str, response_format) -> str:
    try:
        return str(
            client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": ""},
                    {"role": "user", "content": prompt},
                ],
                response_format=response_format,
            )
            .choices[0]
            .message.content
        )
    except Exception as e:
        raise RuntimeError(f"Failed to generate text from OpenAI API: {e}") from e

def generate_text_for_script(prompt: str) -> str:
    refined_prompt = f"""
    Please convert the following text into a script format, following these rules:
    - Every **spoken dialogue** (e.g., "Hello!") should be attributed to the **character** who speaks it.
    - Any **narrative action** (e.g., "she said", "he laughed", "they replied") should **NOT** be included in the character's speech. Instead, it should be assigned to the **Narrator**.
    - Use this format for dialogue: Character: "Dialogue"
    - Use this format for narration: Narrator: Action or description.
    - **Do not include any action phrases like "said", "replied", or "laughed" inside the character's speech**, they should all be under the Narrator's action.
    
    Example:
    "Beatrice smiled." -> Narrator: Beatrice smiled.
    "She said: 'This is a wonderful day.'" -> Beatrice: "This is a wonderful day."

    Text to convert:
    {prompt}
    """
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4-0613",  # Model version you provided in the second function
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": refined_prompt},
            ],
        )

        if response.choices and len(response.choices) > 0:
            message_content = response.choices[0].message.content
            return message_content

        # Handle case where choices are empty or not structured as expected
        raise ValueError("No choices found in the response.")

    except Exception as e:
        raise RuntimeError(f"Failed to generate text from OpenAI API: {e}") from e
