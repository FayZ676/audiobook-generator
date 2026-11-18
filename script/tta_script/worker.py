"""The script step as a RunPod serverless worker.

It keeps nothing between jobs: each job's input carries everything it needs,
and the caller saves what comes back. Two tasks:

build: one chapter's text, the book's cast so far and the voices there are to
give characters, in; the chapter's script and the updated cast out. Build a
book's chapters in order, one at a time, each with the cast the previous one
returned.

    {"task": "build", "text": "...", "cast": {"members": [...]}, "voices": [{"name": ..., "age": ..., "gender": ...}]}
    -> {"script": {"segments": [...]}, "cast": {"members": [...]}}

recheck: a stronger model's speaker for lines of a chapter (segment ids), or,
with none given, for every dialogue line not yet checked.

    {"task": "recheck", "script": {...}, "cast": {...}, "segment_ids": ["seg-0012"]}
    -> {"speakers": {"seg-0012": "c3"}}

A job whose input is wrong comes back as {"error": "..."}, which RunPod
reports as a failed job.

    .venv/bin/python -m tta_script.worker --test_input '{"input": {...}}'
"""

import logging
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from tta_script.cast import Cast, Voice
from tta_script.dialogue.recheck import recheck_segments
from tta_script.pipeline import build_script
from tta_script.script import Script


class BuildJob(BaseModel):
    task: Literal["build"]
    text: str
    cast: Cast = Field(default_factory=Cast)
    voices: list[Voice] = Field(default_factory=list)


class RecheckJob(BaseModel):
    task: Literal["recheck"]
    script: Script
    cast: Cast
    segment_ids: list[str] = Field(default_factory=list)


Job: TypeAdapter[BuildJob | RecheckJob] = TypeAdapter(Annotated[BuildJob | RecheckJob, Field(discriminator="task")])


def handler(job: dict) -> dict:
    try:
        request = Job.validate_python(job["input"])
        if isinstance(request, BuildJob):
            script, cast = build_script(request.text, request.cast, request.voices)
            return {"script": script.model_dump(), "cast": cast.model_dump()}
        return {"speakers": recheck_segments(request.script, request.cast, request.segment_ids)}
    except (ValidationError, ValueError) as e:
        return {"error": str(e)}


if __name__ == "__main__":
    from pathlib import Path

    import runpod  # type: ignore[import-untyped]
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")  # local runs; RunPod sets the keys itself
    logging.basicConfig(level=logging.WARNING)
    runpod.serverless.start({"handler": handler})
