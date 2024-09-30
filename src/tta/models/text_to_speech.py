import os

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text(prompt: str) -> str:
    try:
        return str(
            client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": ""},
                    {"role": "user", "content": prompt},
                ],
            )
            .choices[0]
            .message.content
        )
    except Exception as e:
        raise RuntimeError(f"Failed to generate text from OpenAI API: {e}") from e
