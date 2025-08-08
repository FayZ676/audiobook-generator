import os

from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_text(
    system_prompt: str, prompt: str, response_format, max_retries: int = 3
) -> str:
    last_exception = None
    for _ in range(max_retries):
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
            last_exception = e

    raise RuntimeError(
        f"Failed to generate text from OpenAI API after {max_retries} retries: {last_exception}"
    ) from last_exception
