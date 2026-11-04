import logging
import os
from functools import cache

from pydantic import BaseModel


logger = logging.getLogger(__name__)

# "<provider>:<model>", e.g. "openai:gpt-5-nano" or "anthropic:claude-haiku-5-5".
DEFAULT_MODEL = "anthropic:claude-haiku-5-5"
# Reasoning depth for models that think before answering. Every call in this
# pipeline is classification or extraction, which doesn't benefit from more.
REASONING_EFFORT = "low"


def current_model() -> str:
    return os.getenv("TTA_SCRIPT_MODEL", DEFAULT_MODEL)


def generate_text(
    system_prompt: str,
    prompt: str,
    response_format: type[BaseModel],
    max_retries: int = 3,
) -> str:
    """Return the model's reply as a JSON string matching response_format."""
    provider, model = current_model().split(":", 1)
    call = {"openai": _call_openai, "anthropic": _call_anthropic}.get(provider)
    if call is None:
        raise ValueError(f"Unknown model provider: {provider!r}")

    last_exception = None
    for _ in range(max_retries):
        try:
            return call(model, system_prompt, prompt, response_format)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Model call failed (%s): %s", current_model(), e)
            last_exception = e

    raise RuntimeError(
        f"Failed to generate text from {current_model()} after {max_retries} retries: {last_exception}"
    ) from last_exception


def _call_openai(model, system_prompt, prompt, response_format) -> str:
    # GPT-5-family models reason before answering; older models reject the parameter.
    extra = {"reasoning_effort": REASONING_EFFORT} if model.startswith("gpt-5") else {}
    response = _openai_client().beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        response_format=response_format,
        **extra,
    )
    usage = response.usage
    cached = usage.prompt_tokens_details.cached_tokens if usage.prompt_tokens_details else 0
    _log_usage(model, usage.prompt_tokens - cached, cached, usage.completion_tokens)
    return str(response.choices[0].message.content)


def _call_anthropic(model, system_prompt, prompt, response_format) -> str:
    response = _anthropic_client().messages.parse(
        model=model,
        max_tokens=16000,
        output_config={"effort": REASONING_EFFORT},
        messages=[{"role": "user", "content": prompt}],
        output_format=response_format,
        **({"system": system_prompt} if system_prompt else {}),
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"{model} declined the request: {response.stop_details}")
    usage = response.usage
    _log_usage(
        model,
        usage.input_tokens,
        usage.cache_read_input_tokens or 0,
        usage.output_tokens,
    )
    return response.parsed_output.model_dump_json()


def _log_usage(model: str, input_tokens: int, cached_tokens: int, output_tokens: int):
    # Uncached input, cached input and output tokens, so callers can price a run.
    logger.info(
        "usage model=%s input=%d cached=%d output=%d",
        model,
        input_tokens,
        cached_tokens,
        output_tokens,
        extra={"usage": (model, input_tokens, cached_tokens, output_tokens)},
    )


@cache
def _openai_client():
    from openai import OpenAI  # pylint: disable=import-outside-toplevel

    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@cache
def _anthropic_client():
    import anthropic  # pylint: disable=import-outside-toplevel

    return anthropic.Anthropic()
