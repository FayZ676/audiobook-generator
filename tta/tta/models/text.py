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
