"""OpenAI's Decisions API: the model picks one of the choices you give it and
returns a probability for each, instead of writing free text."""

import logging
import os
from dataclasses import dataclass
from functools import cache

from tta_script.models.text import log_usage


logger = logging.getLogger(__name__)

MAX_QUESTIONS = 400  # per request, per the API reference


@dataclass(frozen=True)
class Choice:
    value: str
    description: str


@dataclass(frozen=True)
class Question:
    name: str
    instructions: str
    choices: tuple[Choice, ...]


@dataclass(frozen=True)
class Answer:
    choice: str | None  # None when the model refused
    confidence: float


def decide(model: str, evidence: str, questions: list[Question]) -> dict[str, Answer]:
    """Ask every question about the same evidence. Returns question name -> answer.

    Questions go in requests of up to MAX_QUESTIONS; each request repeats the
    evidence, which prompt caching makes cheap after the first."""
    answers: dict[str, Answer] = {}
    for start in range(0, len(questions), MAX_QUESTIONS):
        response = _client().decisions.create(
            model=model,
            input=evidence,
            questions=[
                {
                    "type": "choice",
                    "name": q.name,
                    "instructions": q.instructions,
                    "choices": [{"value": c.value, "description": c.description} for c in q.choices],
                }
                for q in questions[start : start + MAX_QUESTIONS]
            ],
        )
        usage = response.usage
        cached = usage.input_tokens_details.cached_tokens
        log_usage(model, usage.input_tokens - cached, cached, usage.output_tokens)
        for answer in response.answers:
            if answer.type == "refusal":
                logger.warning("%s refused question %s", model, answer.name)
                answers[answer.name] = Answer(choice=None, confidence=0.0)
            else:
                answers[answer.name] = Answer(choice=answer.choice, confidence=answer.confidence)
    return answers


@cache
def _client():
    from openai import OpenAI  # pylint: disable=import-outside-toplevel

    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
