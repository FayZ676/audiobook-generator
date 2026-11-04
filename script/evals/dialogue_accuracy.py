"""Score the script pipeline's characters and speaker labels, per model.

Processes Harry Potter chapters 1-3 in order, the way production does: each
chapter's speakers are passed to the next, so a character keeps one voice
across chapters. Scores, per run:

- dialogue accuracy: share of dialogue segments given the right speaker,
  against the hand-checked tests/text/**/harrypotter-N-expected-dialogue.txt
- speaker recall: share of each chapter's speaking characters that were found
- extra characters: characters found that never speak (each costs a voice)
- duplicates: one person split into several characters, such as
  "Mr. Dursley" in chapter 1 and "Uncle Vernon" in chapter 2
- gender / age: share of found speakers whose voice traits are right

Calls paid model APIs, which is why it is a script and not a pytest test.

    .venv/bin/python -m evals.dialogue_accuracy \
        --models anthropic:claude-haiku-5-5 openai:gpt-4.1 --runs 5
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

from tta_types.types import Character, Speaker, Voice
from tta_script.character.extract import get_characters
from tta_script.dialogue.extract import dialogue_to_script, get_dialogues, get_text_segments
from tta_script.speakers import get_speakers
from tta_script.utils.text import normalize_quotes


SCRIPT_DIR = Path(__file__).resolve().parent.parent
TEXT_DIR = SCRIPT_DIR / "tests" / "text"
CHAPTERS = {
    1: (TEXT_DIR / "harrypotter-1.txt", TEXT_DIR / "harrypotter-1-expected-dialogue.txt"),
    2: (
        TEXT_DIR / "chapters" / "harrypotter-2.txt",
        TEXT_DIR / "chapters" / "harrypotter-2-expected-dialogue.txt",
    ),
    3: (
        TEXT_DIR / "chapters" / "harrypotter-3.txt",
        TEXT_DIR / "chapters" / "harrypotter-3-expected-dialogue.txt",
    ),
}

# Every character who speaks in chapters 1-3, keyed by the name the expected
# files use. "aliases" are the names the pipeline may legitimately use (chapter
# 1 only ever says "Mr. Dursley"; chapter 2 says "Uncle Vernon"). "ages" lists
# every acceptable age group, since some characters sit between two.
CHARACTERS = {
    "Uncle Vernon": {
        "aliases": {"Uncle Vernon", "Vernon", "Vernon Dursley", "Mr. Dursley"},
        "gender": "male",
        "ages": {"middle-aged"},
    },
    "Mrs. Dursley": {
        "aliases": {"Mrs. Dursley", "Aunt Petunia", "Petunia", "Petunia Dursley"},
        "gender": "female",
        "ages": {"middle-aged"},
    },
    "Dudley": {
        "aliases": {"Dudley", "Dudley Dursley", "Duddy"},
        "gender": "male",
        "ages": {"young"},
    },
    "Harry Potter": {
        "aliases": {"Harry Potter", "Harry", "Mr. H. Potter"},
        "gender": "male",
        "ages": {"young"},
    },
    "Piers Polkiss": {
        "aliases": {"Piers Polkiss", "Piers"},
        "gender": "male",
        "ages": {"young"},
    },
    "Professor McGonagall": {
        "aliases": {"Professor McGonagall", "McGonagall", "Minerva McGonagall"},
        "gender": "female",
        "ages": {"middle-aged", "old"},
    },
    "Albus Dumbledore": {
        "aliases": {"Albus Dumbledore", "Dumbledore", "Professor Dumbledore", "Albus"},
        "gender": "male",
        "ages": {"old"},
    },
    "Hagrid": {
        "aliases": {"Hagrid", "Rubeus Hagrid"},
        "gender": "male",
        "ages": {"middle-aged", "old"},
    },
}
NARRATOR = "Narrator"

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


def load_expected(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
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


def who_is(character: Character) -> str | None:
    """The expected character this predicted character stands for, if any."""
    if NARRATOR in character.names:
        return NARRATOR
    names = set(character.names)
    return next((key for key, c in CHARACTERS.items() if names & c["aliases"]), None)


def score_labels(segments, dialogue, expected) -> dict:
    if [d.text for d in dialogue] != [e[1] for e in expected]:
        raise RuntimeError("Segments no longer line up with the expected file.")
    total = correct = 0
    mistakes = []
    for i, (segment, line, (want, _)) in enumerate(zip(segments, dialogue, expected)):
        got = who_is(line.speaker.character)
        if segment.is_dialogue:
            total += 1
            correct += got == want
        if got != want:
            mistakes.append(
                {"index": i, "expected": want, "got": line.speaker.character.names, "text": line.text}
            )
    return {"dialogue_total": total, "dialogue_correct": correct, "mistakes": mistakes}


def score_characters(new: set[Character], known: set[Character], expected) -> dict:
    """Score the characters known after a chapter: everything carried over
    from earlier chapters plus what this chapter found."""
    speaking = {want for want, _ in expected if want != NARRATOR}
    everyone = known | new
    found = {who_is(c) for c in everyone} - {None, NARRATOR}

    by_person: dict[str, list[Character]] = {}
    for c in everyone:
        if (key := who_is(c)) not in (None, NARRATOR):
            by_person.setdefault(key, []).append(c)

    traits = [
        (c.gender == CHARACTERS[key]["gender"], c.age in CHARACTERS[key]["ages"], key, c)
        for c in new
        if (key := who_is(c)) not in (None, NARRATOR)
    ]
    return {
        "speakers": len(speaking),
        "speakers_found": len(speaking & found),
        "missing": sorted(speaking - found),
        "extras": sorted(c.first_alias() for c in new if who_is(c) is None),
        "duplicates": {k: [c.names for c in cs] for k, cs in by_person.items() if len(cs) > 1},
        "gender_right": sum(t[0] for t in traits),
        "age_right": sum(t[1] for t in traits),
        "traits_checked": len(traits),
        "wrong_traits": [
            {"who": key, "age": c.age, "gender": c.gender} for g, a, key, c in traits if not (g and a)
        ],
    }


def run_once(chapters: list[int]) -> dict:
    voices = fake_voices()
    known_speakers: set[Speaker] = set()
    per_chapter = {}
    for number in chapters:
        text_path, expected_path = CHAPTERS[number]
        text = normalize_quotes(text_path.read_text(encoding="utf-8"))
        expected = load_expected(expected_path)

        # Same steps as tta_script.rp_handler.handler.
        known = {s.character for s in known_speakers}
        new = get_characters(text, known)
        speakers = get_speakers(
            characters=known | new,
            voices=voices,
            narrator_voice=voices[0],
            previous_speakers=known_speakers,
        )
        segments = get_text_segments(text)
        dialogue = get_dialogues(text_segments=segments, speakers=speakers)

        per_chapter[number] = {
            **score_labels(segments, dialogue, expected),
            **score_characters(new, known, expected),
            "characters": sorted(sorted(c.names) for c in new),
        }
        known_speakers |= set(dialogue_to_script(dialogue).speakers)
    return {"chapters": per_chapter, **totals(per_chapter)}


def totals(per_chapter: dict) -> dict:
    def total(key):
        return sum(c[key] for c in per_chapter.values())

    last = per_chapter[max(per_chapter)]
    return {
        "dialogue": total("dialogue_correct") / total("dialogue_total"),
        "recall": total("speakers_found") / total("speakers"),
        "extras": sum(len(c["extras"]) for c in per_chapter.values()),
        # Characters accumulate, so the last chapter sees every duplicate.
        "duplicates": len(last["duplicates"]),
        "gender": total("gender_right") / max(1, total("traits_checked")),
        "age": total("age_right") / max(1, total("traits_checked")),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("--models", nargs="+", required=True, help='e.g. "openai:gpt-5-nano"')
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--chapters", nargs="+", type=int, default=list(CHAPTERS))
    parser.add_argument("--out", type=Path, default=SCRIPT_DIR / "evals" / "results")
    args = parser.parse_args()

    load_dotenv(SCRIPT_DIR / ".env.local")
    logging.basicConfig(level=logging.WARNING)
    collector = UsageCollector()
    usage_logger = logging.getLogger("tta_script.models.text")
    usage_logger.setLevel(logging.INFO)
    usage_logger.addHandler(collector)
    usage_logger.propagate = False  # collect usage without printing every call

    results: dict[str, list[dict]] = {}
    for model in args.models:
        os.environ["TTA_SCRIPT_MODEL"] = model
        results[model] = []
        for run in range(1, args.runs + 1):
            collector.calls.clear()
            started = time.monotonic()
            try:
                result = run_once(args.chapters)
            except Exception as e:  # pylint: disable=broad-exception-caught
                result = {"error": f"{type(e).__name__}: {e}"}
            result["seconds"] = round(time.monotonic() - started, 1)
            result["cost"] = collector.cost()
            result["calls"] = list(collector.calls)
            results[model].append(result)
            print(f"{model} run {run}: {summarise(result)}", flush=True)

    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{datetime.now():%Y%m%d-%H%M%S}.json"
    out_file.write_text(json.dumps({"chapters": args.chapters, "results": results}, indent=2))
    print_table(results)
    print(f"\nPer-segment mistakes and characters: {out_file}")


def summarise(result: dict) -> str:
    if "error" in result:
        return f"FAILED after {result['seconds']}s: {result['error']}"
    chapters = ", ".join(
        f"ch{n} {c['dialogue_correct']}/{c['dialogue_total']}" for n, c in result["chapters"].items()
    )
    cost = f"${result['cost']:.4f}" if result["cost"] is not None else "$?"
    return (
        f"dialogue {result['dialogue']:.1%} ({chapters}), recall {result['recall']:.0%}, "
        f"extras {result['extras']}, duplicates {result['duplicates']}, "
        f"gender {result['gender']:.0%}, age {result['age']:.0%}, {cost}, {result['seconds']}s"
    )


def print_table(results: dict[str, list[dict]]):
    header = (
        f"\n{'model':28} {'dialogue (min-max)':>22} {'recall':>7} {'extras':>7}"
        f" {'dupes':>6} {'gender':>7} {'age':>6} {'$/run':>8} {'s/run':>6} {'failed':>6}"
    )
    print(header)
    for model, runs in results.items():
        ok = [r for r in runs if "error" not in r]
        failed = len(runs) - len(ok)
        if not ok:
            print(f"{model:28} {'all runs failed':>22}{'':>58} {failed:>6}")
            continue

        def mean(key, runs=ok):
            return statistics.mean(r[key] for r in runs)

        acc = [r["dialogue"] for r in ok]
        costs = [r["cost"] for r in ok if r["cost"] is not None]
        cost = f"{statistics.mean(costs):.4f}" if costs else "?"
        spread = f"{statistics.mean(acc):.1%} ({min(acc):.1%}-{max(acc):.1%})"
        print(
            f"{model:28} {spread:>22} {mean('recall'):>7.0%} {mean('extras'):>7.1f}"
            f" {mean('duplicates'):>6.1f} {mean('gender'):>7.0%} {mean('age'):>6.0%}"
            f" {cost:>8} {mean('seconds'):>6.0f} {failed:>6}"
        )


if __name__ == "__main__":
    main()
