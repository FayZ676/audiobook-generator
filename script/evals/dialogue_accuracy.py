"""Score how accurately the script pipeline assigns speakers, per model.

Runs the real pipeline (character extraction -> speakers -> dialogue labelling)
on Harry Potter chapter 1 and compares every segment's speaker with the labels
in tests/text/harrypotter-1-expected-dialogue.txt. Calls paid model APIs.

    .venv/bin/python -m evals.dialogue_accuracy \
        --models openai:gpt-4.1 openai:gpt-5-nano anthropic:claude-haiku-5-5 --runs 5
"""

import argparse
import json
import logging
import os
import statistics
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from tta_types.types import Voice
from tta_script.character.extract import get_characters
from tta_script.dialogue.extract import get_dialogues, get_text_segments
from tta_script.speakers import get_speakers
from tta_script.utils.text import normalize_quotes


SCRIPT_DIR = Path(__file__).resolve().parent.parent
TEXT_DIR = SCRIPT_DIR / "tests" / "text"
CHAPTER = TEXT_DIR / "harrypotter-1.txt"
EXPECTED = TEXT_DIR / "harrypotter-1-expected-dialogue.txt"

# Names the pipeline may legitimately use for each expected speaker.
# Chapter 1 never says "Uncle Vernon", for example, only "Mr. Dursley".
ALIASES = {
    "Narrator": {"Narrator"},
    "Uncle Vernon": {"Uncle Vernon", "Vernon", "Vernon Dursley", "Mr. Dursley"},
    "Mrs. Dursley": {"Mrs. Dursley", "Aunt Petunia", "Petunia", "Petunia Dursley"},
    "Professor McGonagall": {"Professor McGonagall", "McGonagall", "Minerva McGonagall"},
    "Albus Dumbledore": {"Albus Dumbledore", "Dumbledore", "Professor Dumbledore", "Albus"},
    "Hagrid": {"Hagrid", "Rubeus Hagrid"},
    "Dudley": {"Dudley", "Dudley Dursley"},
}

# Listed prices per million tokens: (input, cached input, output). Verify
# against the providers' pricing pages before trusting the cost column.
PRICES = {
    "gpt-4.1": (2.00, 0.50, 8.00),
    "gpt-5-mini": (0.25, 0.025, 2.00),
    "gpt-5-nano": (0.05, 0.005, 0.40),
    "claude-haiku-5-5": (0.10, 0.01, 0.50),
}


class UsageCollector(logging.Handler):
    """Collects the token usage that tta_script.models.text logs per call."""

    def __init__(self):
        super().__init__()
        self.calls: list[tuple[str, int, int, int]] = []

    def emit(self, record):
        if hasattr(record, "usage"):
            self.calls.append(record.usage)

    def cost(self) -> float | None:
        total = 0.0
        for model, uncached, cached, output in self.calls:
            if model not in PRICES:
                return None
            p_in, p_cached, p_out = PRICES[model]
            total += (uncached * p_in + cached * p_cached + output * p_out) / 1e6
        return total


def load_expected() -> list[tuple[str, str]]:
    lines = EXPECTED.read_text(encoding="utf-8").splitlines()
    return [tuple(s.strip() for s in line.split(":", 1)) for line in lines if line]


def fake_voices() -> list[Voice]:
    """Enough voices for every age/gender pair, so no character falls back to
    the narrator's voice. Voices don't affect scoring; speakers do."""
    return [
        Voice(name=f"{age}-{gender}-{i}", age=age, gender=gender, audio_path="", audio_transcript="")
        for i in range(4)
        for age in ("middle-aged", "young", "old")
        for gender in ("male", "female")
    ]


def run_once(text: str, expected: list[tuple[str, str]]) -> dict:
    characters = get_characters(text, set())
    voices = fake_voices()
    speakers = get_speakers(
        characters=characters, voices=voices, narrator_voice=voices[0], previous_speakers=set()
    )
    segments = get_text_segments(text)
    dialogue = get_dialogues(text_segments=segments, speakers=speakers)

    if [d.text for d in dialogue] != [e[1] for e in expected]:
        raise RuntimeError("Segments no longer line up with the expected file.")

    mistakes = []
    dialogue_total = dialogue_correct = 0
    for i, (segment, line, (want, _)) in enumerate(zip(segments, dialogue, expected)):
        got = set(line.speaker.character.names)
        correct = bool(got & ALIASES[want])
        if segment.is_dialogue:
            dialogue_total += 1
            dialogue_correct += correct
        if not correct:
            mistakes.append({"index": i, "expected": want, "got": sorted(got), "text": line.text})

    return {
        "overall": 1 - len(mistakes) / len(expected),
        "dialogue": dialogue_correct / dialogue_total,
        "characters": sorted(sorted(c.names) for c in characters),
        "mistakes": mistakes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("--models", nargs="+", required=True, help='e.g. "openai:gpt-5-nano"')
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--out", type=Path, default=SCRIPT_DIR / "evals" / "results")
    args = parser.parse_args()

    load_dotenv(SCRIPT_DIR / ".env.local")
    logging.basicConfig(level=logging.WARNING)
    collector = UsageCollector()
    usage_logger = logging.getLogger("tta_script.models.text")
    usage_logger.setLevel(logging.INFO)
    usage_logger.addHandler(collector)
    usage_logger.propagate = False  # collect usage without printing every call

    text = normalize_quotes(CHAPTER.read_text(encoding="utf-8"))
    expected = load_expected()
    results: dict[str, list[dict]] = {}

    for model in args.models:
        os.environ["TTA_SCRIPT_MODEL"] = model
        results[model] = []
        for run in range(1, args.runs + 1):
            collector.calls.clear()
            started = time.monotonic()
            try:
                result = run_once(text, expected)
            except Exception as e:  # pylint: disable=broad-exception-caught
                result = {"error": str(e)}
            result["seconds"] = round(time.monotonic() - started, 1)
            result["cost"] = collector.cost()
            result["calls"] = list(collector.calls)
            results[model].append(result)
            print(f"{model} run {run}: {summarise(result)}", flush=True)

    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{datetime.now():%Y%m%d-%H%M%S}.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print(f"\n{'model':32} {'dialogue acc (min-max)':>24} {'overall':>8} {'$/run':>8} {'s/run':>6} {'failed':>6}")
    for model, runs in results.items():
        ok = [r for r in runs if "error" not in r]
        failed = len(runs) - len(ok)
        if not ok:
            print(f"{model:32} {'all runs failed':>24} {'':>8} {'':>8} {'':>6} {failed:>6}")
            continue
        acc = [r["dialogue"] for r in ok]
        costs = [r["cost"] for r in ok if r["cost"] is not None]
        cost = f"{statistics.mean(costs):.4f}" if costs else "?"
        spread = f"{statistics.mean(acc):.1%} ({min(acc):.1%}-{max(acc):.1%})"
        print(
            f"{model:32} {spread:>24} {statistics.mean(r['overall'] for r in ok):>8.1%}"
            f" {cost:>8} {statistics.mean(r['seconds'] for r in ok):>6.0f} {failed:>6}"
        )
    print(f"\nPer-segment mistakes: {out_file}")


def summarise(result: dict) -> str:
    if "error" in result:
        return f"FAILED after {result['seconds']}s: {result['error']}"
    cost = f"${result['cost']:.4f}" if result["cost"] is not None else "$?"
    return (
        f"dialogue {result['dialogue']:.1%}, overall {result['overall']:.1%}, "
        f"{len(result['mistakes'])} mistakes, {cost}, {result['seconds']}s"
    )


if __name__ == "__main__":
    main()
