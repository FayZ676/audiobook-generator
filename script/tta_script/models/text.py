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
MAX_RETRIES = 3


def current_model() -> str:
    return os.getenv("TTA_SCRIPT_MODEL", DEFAULT_MODEL)


def generate_text(  # pylint: disable=too-many-arguments
    system_prompt: str,
    prompt: str,
    response_format: type[BaseModel],
    *,
    model_name: str | None = None,
    effort: str = REASONING_EFFORT,
    cached_prefix: str = "",
) -> str:
    """Return the model's reply as a JSON string matching response_format.

    model_name ("<provider>:<model>") and effort override the defaults, for
    the few calls that need a stronger model thinking harder. cached_prefix
    goes before prompt and is cached (Anthropic only), so calls sharing it
    within a few minutes pay a fraction for it."""
    model_name = model_name or current_model()
    provider, model = model_name.split(":", 1)
    call = {"openai": _call_openai, "anthropic": _call_anthropic}.get(provider)
    if call is None:
        raise ValueError(f"Unknown model provider: {provider!r}")

    last_exception = None
    for _ in range(MAX_RETRIES):
        try:
            return call(model, system_prompt, prompt, response_format, effort, cached_prefix)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.warning("Model call failed (%s): %s", model_name, e)
            last_exception = e

    raise RuntimeError(
        f"Failed to generate text from {model_name} after {MAX_RETRIES} retries: {last_exception}"
    ) from last_exception


def _call_openai(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    model, system_prompt, prompt, response_format, effort, cached_prefix
) -> str:
    prompt = cached_prefix + prompt  # OpenAI caches long prefixes by itself
    # GPT-5-family models reason before answering; older models reject the parameter.
    extra = {"reasoning_effort": effort} if model.startswith("gpt-5") else {}
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
    log_usage(model, usage.prompt_tokens - cached, cached, usage.completion_tokens)
    return str(response.choices[0].message.content)


def _call_anthropic(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    model, system_prompt, prompt, response_format, effort, cached_prefix
) -> str:
    content: list[dict] = [{"type": "text", "text": prompt}]
    if cached_prefix:
        content.insert(0, {"type": "text", "text": cached_prefix, "cache_control": {"type": "ephemeral"}})
    response = _anthropic_client().messages.parse(
        model=model,
        max_tokens=16000,
        output_config={"effort": effort},
        messages=[{"role": "user", "content": content}],
        output_format=response_format,
        **({"system": system_prompt} if system_prompt else {}),
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"{model} declined the request: {response.stop_details}")
    usage = response.usage
    log_usage(
        model,
        usage.input_tokens,
        usage.cache_read_input_tokens or 0,
        usage.output_tokens,
    )
    return response.parsed_output.model_dump_json()


def log_usage(model: str, input_tokens: int, cached_tokens: int, output_tokens: int):
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
