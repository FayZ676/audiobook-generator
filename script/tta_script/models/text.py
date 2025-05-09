import os

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text(system_prompt: str, prompt: str, response_format) -> str:
    try:
        return str(
            client.beta.chat.completions.parse(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                response_format=response_format,
            )
            .choices[0]
            .message.content
        )
    except Exception as e:
        raise RuntimeError(f"Failed to generate text from OpenAI API: {e}") from e
