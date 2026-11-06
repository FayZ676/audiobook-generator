"""Score the script pipeline's characters and speaker labels, per model.

Runs every book in evals/books/ (or those named with --books). A book's
chapters run in order, the way a user would build them: each chapter's cast
is passed to the next, so a character keeps one voice. Each book starts with
an empty cast. Scores, per run:

- dialogue accuracy: share of dialogue segments given the right speaker
- missed dialogue: segments the splitter left as narration that someone
  speaks (a quote spanning paragraphs, say); the narrator reads them, wrongly
- speaker recall: share of each chapter's speaking characters that were found
- extra characters: characters found that never speak (each costs a voice)
- names: whether new names (Harry Potter chapter 2's "Uncle Vernon") join the
  right character
- duplicates: one person split into several characters, such as
  "Mr. Dursley" in chapter 1 and "Uncle Vernon" in chapter 2
- gender / age: share of found speakers whose voice traits are right

A book folder holds, per chapter, NN.txt and its hand-checked labels
NN-expected.txt (one "Speaker: segment text" line per segment), plus
characters.json:

- characters: every speaking character, keyed by the name the expected files
  use. "aliases" are names the pipeline may legitimately give them; "ages"
  lists every acceptable age group, since some characters sit between two.
- name_links: per chapter number, names that chapter uses heavily which the
  cast must attach to the right character by the end of it.

Labelling rules, so every book is labelled the same way:

- Quoted thoughts belong to the thinker ("Very uncomfortable," thought Alice).
- Words quoted but not spoken aloud belong to the narrator: a word being
  mentioned (the "pecking" ended), something left unsaid (she didn't say
  "perhaps never"), words imagined on someone's lips.
- Lines a group speaks together ("No room!" they cried) belong to the narrator.
- A speaker known only by description ("Scrooge's nephew", "the keeper") is a
  character like any other. Only voices that can't be told apart ("a voice
  cried") belong to the narrator.
- A letter read aloud belongs to the reader.
- In a first-person book the narrator is a character: their own spoken lines
  belong to the narrator, so one voice reads all of them (Watson's "said I").
- Speech the splitter leaves inside narration is still labelled with its
  speaker, which is what the missed dialogue count measures.

Calls paid model APIs, which is why it is a script and not a pytest test.

--models picks the model that finds characters; --label-model the speaker
labeller (default: the Decisions API, which also reports confidence).

    .venv/bin/python -m evals.dialogue_accuracy --runs 5
    .venv/bin/python -m evals.dialogue_accuracy --books alice --runs 1
    .venv/bin/python -m evals.dialogue_accuracy --label-model anthropic:claude-haiku-5-5
"""

import argparse
import json
import logging
import os
import statistics
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from tta_script.cast import NARRATOR_ID, Cast, CastMember, Voice
from tta_script.script import Script, ScriptSegment
from tta_script.dialogue.extract import DEFAULT_LABEL_MODEL, get_text_segments
from tta_script.models.text import DEFAULT_MODEL
from tta_script.pipeline import build_script


SCRIPT_DIR = Path(__file__).resolve().parent.parent
BOOKS_DIR = SCRIPT_DIR / "evals" / "books"
NARRATOR = "Narrator"


@dataclass
class Chapter:
    number: int
    text: Path
    expected: Path


@dataclass
class Book:
    name: str
    chapters: list[Chapter]
    characters: dict[str, dict]
    name_links: dict[int, dict[str, str]]

    @classmethod
    def load(cls, folder: Path) -> "Book":
        data = json.loads((folder / "characters.json").read_text(encoding="utf-8"))
        chapters = [
            Chapter(int(p.name.split("-")[0]), folder / p.name.replace("-expected", ""), p)
            for p in sorted(folder.glob("*-expected.txt"))
        ]
        characters = {
            name: {**c, "aliases": {name_key(a) for a in c["aliases"]}, "ages": set(c["ages"])}
            for name, c in data["characters"].items()
        }
        links = {int(n): names for n, names in data.get("name_links", {}).items()}
        return cls(folder.name, chapters, characters, links)

    def who_is(self, member: CastMember | None) -> str | None:
        """The expected character this cast member stands for, if any."""
        if member is None:
            return None
        if member.id == NARRATOR_ID:
            return NARRATOR
        names = {name_key(n) for n in member.names}
        exact = next((key for key, c in self.characters.items() if names & c["aliases"]), None)
        if exact is not None:
            return exact
        # Unnamed characters are described differently each run ("the tiny
        # old man" for "old man"), so fall back to overlapping descriptions.
        # Single words are left out: "Bingley" would match "Miss Bingley".
        descriptions = [n for n in names if len(n.split()) > 1]
        return next(
            (
                key
                for key, c in self.characters.items()
                if any(names_overlap(n, a) for n in descriptions for a in c["aliases"])
            ),
            None,
        )


def name_key(name: str) -> str:
    """Names match ignoring case and a leading "the": "the Hatter" is "Hatter"."""
    return name.lower().removeprefix("the ").strip()


def names_overlap(a: str, b: str) -> bool:
    """One name's words contain the other's: "Josephine" and "Josephine March",
    "Aunt Petunia" and "Petunia". Either tells the labeller who is meant."""
    words_a, words_b = set(name_key(a).split()), set(name_key(b).split())
    return words_a <= words_b or words_b <= words_a


def all_books() -> list[str]:
    return sorted(p.name for p in BOOKS_DIR.iterdir() if (p / "characters.json").exists())


# Listed prices per million tokens: (input, cached input, output). Verify
# against the providers' pricing pages before trusting the cost column.
PRICES = {
    "gpt-4.1": (2.00, 0.50, 8.00),
    "gpt-5-mini": (0.25, 0.025, 2.00),
    "gpt-5-nano": (0.05, 0.005, 0.40),
    "claude-haiku-5-5": (0.10, 0.01, 0.50),
    "gpt-6-luna": (0.10, 0.01, 0.0),  # Decisions API: output is free
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


def align(script: Script, expected) -> list[ScriptSegment] | None:
    """The script's segment for each expected one, or None if they line up
    exactly. Where the model finds the speech (a text without quote marks),
    its segments start and end in slightly different places, so each
    expected segment takes the script segment covering most of its letters."""
    if [s.text for s in script.segments] == [e[1] for e in expected]:
        return None
    owner = [k for k, s in enumerate(script.segments) for c in s.text if c.isalnum()]
    lines, at = [], 0
    for _, text in expected:
        span = owner[at : at + sum(c.isalnum() for c in text)]
        at += len(span)
        if not span:
            raise RuntimeError(f"Expected segment {text[:40]!r} is not in the script.")
        lines.append(script.segments[Counter(span).most_common(1)[0][0]])
    if at != len(owner):
        raise RuntimeError("The script's text differs from the expected file's.")
    return lines


def dialogue_flags(lined_up: bool, segments, expected) -> list[bool]:
    """Which expected segments are dialogue. When the script lines up with
    the expected file, the splitter says. Otherwise (the model found the
    speech) dialogue is whatever a character says, and missed dialogue is
    speech the narrator reads."""
    if lined_up:
        return [s.is_dialogue for s in segments]
    return [want != NARRATOR for want, _ in expected]


def missed_dialogue(lined_up: bool, is_dialogue: list[bool], lines, expected) -> int:
    """Speech the narrator reads: left as narration by the splitter, or (when
    the model found the speech) given to the narrator."""
    if lined_up:
        return sum(not d and want != NARRATOR for d, (want, _) in zip(is_dialogue, expected))
    return sum(w != NARRATOR and line.speaker_id == NARRATOR_ID for line, (w, _) in zip(lines, expected))


def score_labels(book: Book, script: Script, cast: Cast, segments, expected) -> dict:
    aligned = align(script, expected)
    lines = aligned or script.segments
    is_dialogue = dialogue_flags(aligned is None, segments, expected)
    got = [book.who_is(cast.get(line.speaker_id)) for line in lines]
    right = [g == want for g, (want, _) in zip(got, expected)]
    return {
        "dialogue_total": sum(is_dialogue),
        "dialogue_correct": sum(d and r for d, r in zip(is_dialogue, right)),
        "missed_dialogue": missed_dialogue(aligned is None, is_dialogue, lines, expected),
        "mistakes": [
            {"index": i, "expected": want, "got": speaker_names(cast, line), "text": text}
            for i, (line, (want, text), r) in enumerate(zip(lines, expected, right))
            if not r
        ],
        "confidences": [
            (line.confidence, r)
            for line, d, r in zip(lines, is_dialogue, right)
            if d and line.confidence is not None
        ],
    }


def speaker_names(cast: Cast, line: ScriptSegment) -> list[str] | str:
    member = cast.get(line.speaker_id)
    return member.names if member else line.speaker_id


def score_characters(book: Book, before: Cast, after: Cast, number: int, expected) -> dict:
    """Score the cast after a chapter against who speaks in it."""
    speaking = {want for want, _ in expected if want != NARRATOR}
    members = [m for m in after.members if m.id != NARRATOR_ID]
    new = [m for m in members if before.get(m.id) is None]

    by_person: dict[str, list[CastMember]] = {}
    for m in members:
        if (key := book.who_is(m)) is not None:
            by_person.setdefault(key, []).append(m)

    traits = [
        (m.gender == book.characters[key]["gender"], m.age in book.characters[key]["ages"], key, m)
        for m in new
        if (key := book.who_is(m)) is not None
    ]
    links = book.name_links.get(number, {})
    unlinked = [
        f"{key} lacks {name!r}"
        for key, name in links.items()
        if not any(names_overlap(name, n) for m in by_person.get(key, []) for n in m.names)
    ]
    return {
        "speakers": len(speaking),
        "speakers_found": len(speaking & set(by_person)),
        "missing": sorted(speaking - set(by_person)),
        "extras": sorted(m.name for m in new if book.who_is(m) is None),
        "duplicates": {k: [m.names for m in ms] for k, ms in by_person.items() if len(ms) > 1},
        "names_checked": len(links),
        "names_linked": len(links) - len(unlinked),
        "unlinked": unlinked,
        "gender_right": sum(t[0] for t in traits),
        "age_right": sum(t[1] for t in traits),
        "traits_checked": len(traits),
        "wrong_traits": [
            {"who": key, "age": m.age, "gender": m.gender} for g, a, key, m in traits if not (g and a)
        ],
    }


def run_once(books: list[Book]) -> dict:
    voices = fake_voices()
    per_chapter = {}
    for book in books:
        cast = Cast()
        for chapter in book.chapters:
            text = chapter.text.read_text(encoding="utf-8")
            expected = load_expected(chapter.expected)

            before = cast
            script, cast = build_script(text, cast, voices)
            segments = get_text_segments(text)

            per_chapter[f"{book.name} ch{chapter.number}"] = {
                **score_labels(book, script, cast, segments, expected),
                **score_characters(book, before, cast, chapter.number, expected),
                "cast": [m.model_dump() for m in cast.members],
                "last_of_book": chapter is book.chapters[-1],
            }
    return {"chapters": per_chapter, **totals(per_chapter)}


def totals(per_chapter: dict) -> dict:
    def total(key):
        return sum(c[key] for c in per_chapter.values())

    return {
        "dialogue": total("dialogue_correct") / total("dialogue_total"),
        "missed_dialogue": total("missed_dialogue"),
        "recall": total("speakers_found") / total("speakers"),
        "extras": sum(len(c["extras"]) for c in per_chapter.values()),
        # A book's cast accumulates, so its last chapter sees every duplicate.
        "duplicates": sum(len(c["duplicates"]) for c in per_chapter.values() if c["last_of_book"]),
        # With nothing to check, nothing is wrong.
        "names": share(total("names_linked"), total("names_checked")),
        "gender": share(total("gender_right"), total("traits_checked")),
        "age": share(total("age_right"), total("traits_checked")),
        **calibration([pair for c in per_chapter.values() for pair in c["confidences"]]),
    }


def share(part: int, whole: int) -> float:
    return part / whole if whole else 1.0


def calibration(pairs: list[tuple[float, bool]]) -> dict:
    """If a person reviews the least confident lines, how many mistakes do
    they catch? catch10 = share of all mistakes in the least confident 10%."""
    if not pairs:
        return {"catch10": None, "catch20": None}
    mistakes = sum(not right for _, right in pairs)
    ranked = sorted(pairs, key=lambda p: p[0])

    def catch(share: float) -> float | None:
        flagged = ranked[: max(1, round(len(ranked) * share))]
        return sum(not right for _, right in flagged) / mistakes if mistakes else None

    right = [c for c, ok in pairs if ok]
    wrong = [c for c, ok in pairs if not ok]
    return {
        "catch10": catch(0.10),
        "catch20": catch(0.20),
        "confidence_right": statistics.mean(right) if right else None,
        "confidence_wrong": statistics.mean(wrong) if wrong else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument(
        "--models",
        nargs="+",
        default=[DEFAULT_MODEL],
        help=f'character-finding models (default "{DEFAULT_MODEL}"), e.g. "openai:gpt-4.1"',
    )
    parser.add_argument(
        "--label-model",
        default=DEFAULT_LABEL_MODEL,
        help=f'speaker labeller (default "{DEFAULT_LABEL_MODEL}"); pass an LLM such as '
        '"anthropic:claude-haiku-5-5" to label with it',
    )
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--books", nargs="+", choices=all_books(), default=all_books())
    parser.add_argument("--out", type=Path, default=SCRIPT_DIR / "evals" / "results")
    args = parser.parse_args()

    load_dotenv(SCRIPT_DIR / ".env.local")
    logging.basicConfig(level=logging.WARNING)
    collector = UsageCollector()
    usage_logger = logging.getLogger("tta_script.models.text")
    usage_logger.setLevel(logging.INFO)
    usage_logger.addHandler(collector)
    usage_logger.propagate = False  # collect usage without printing every call

    books = [Book.load(BOOKS_DIR / name) for name in args.books]
    results: dict[str, list[dict]] = {}
    os.environ["TTA_LABEL_MODEL"] = args.label_model
    for script_model in args.models:
        os.environ["TTA_SCRIPT_MODEL"] = script_model
        model = f"{script_model} + {args.label_model}"
        results[model] = []
        for run in range(1, args.runs + 1):
            collector.calls.clear()
            started = time.monotonic()
            try:
                result = run_once(books)
            except Exception as e:  # pylint: disable=broad-exception-caught
                result = {"error": f"{type(e).__name__}: {e}"}
            result["seconds"] = round(time.monotonic() - started, 1)
            result["cost"] = collector.cost()
            result["calls"] = list(collector.calls)
            results[model].append(result)
            print(f"{model} run {run}: {summarise(result)}", flush=True)

    args.out.mkdir(parents=True, exist_ok=True)
    out_file = args.out / f"{datetime.now():%Y%m%d-%H%M%S}.json"
    out_file.write_text(json.dumps({"books": args.books, "results": results}, indent=2))
    print_table(results)
    for model, runs in results.items():
        catches = [r for r in runs if r.get("catch10") is not None]
        if catches:
            print(
                f"{model}: reviewing the least confident 10% / 20% of dialogue catches "
                f"{statistics.mean(r['catch10'] for r in catches):.0%} / "
                f"{statistics.mean(r['catch20'] for r in catches):.0%} of mistakes"
            )
    print(f"\nPer-segment mistakes and characters: {out_file}")


def summarise(result: dict) -> str:
    if "error" in result:
        return f"FAILED after {result['seconds']}s: {result['error']}"
    chapters = ", ".join(
        f"{name} {c['dialogue_correct']}/{c['dialogue_total']}" for name, c in result["chapters"].items()
    )
    cost = f"${result['cost']:.4f}" if result["cost"] is not None else "$?"
    return (
        f"dialogue {result['dialogue']:.1%} ({chapters}), missed dialogue {result['missed_dialogue']}, recall {result['recall']:.0%}, "
        f"extras {result['extras']}, duplicates {result['duplicates']}, names {result['names']:.0%}, "
        f"gender {result['gender']:.0%}, age {result['age']:.0%}, {catch_text(result)}"
        f"{cost}, {result['seconds']}s"
    )


def catch_text(result: dict) -> str:
    if result.get("catch10") is None:
        return ""
    return (
        f"review 10%/20% catches {result['catch10']:.0%}/{result['catch20']:.0%} of mistakes "
        f"(confidence right {result['confidence_right']:.2f}, "
        f"wrong {result['confidence_wrong'] or 0:.2f}), "
    )


def print_table(results: dict[str, list[dict]]):
    header = (
        f"\n{'model':28} {'dialogue (min-max)':>22} {'recall':>7} {'extras':>7}"
        f" {'dupes':>6} {'names':>6} {'gender':>7} {'age':>6} {'$/run':>8} {'s/run':>6} {'failed':>6}"
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
            f" {mean('duplicates'):>6.1f} {mean('names'):>6.0%} {mean('gender'):>7.0%} {mean('age'):>6.0%}"
            f" {cost:>8} {mean('seconds'):>6.0f} {failed:>6}"
        )


if __name__ == "__main__":
    main()
