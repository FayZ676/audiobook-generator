"""Build a whole book's scripts, chapter by chapter, and report what a user
would get: the cast at the end, cost and time, and how many lines a person
reviewing would be asked to check.

The chapters are NN.txt files in one folder, run in order with the cast
carried from each chapter to the next. A chapter that also has an eval
book's NN-expected.txt (--book) is scored, which shows how many of its
mistakes the low-confidence lines contain.

Writes, to --out: NN-script.txt per chapter (dialogue lines show the
speaker and the labeller's confidence), cast.json, and report.md.

    .venv/bin/python -m evals.whole_book path/to/chapters --book alice --out path/to/out
"""

import argparse
import logging
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv

from evals.dialogue_accuracy import (
    BOOKS_DIR,
    SCRIPT_DIR,
    Book,
    collect_usage,
    fake_voices,
    load_expected,
    names_overlap,
    score_labels,
)
from tta_script.cast import NARRATOR_ID, Cast
from tta_script.dialogue.extract import get_text_segments
from tta_script.pipeline import build_script
from tta_script.script import Script

# Dialogue lines below this confidence are the ones a reviewer is shown.
REVIEW_BELOW = 0.9


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("chapters", type=Path, help="folder of NN.txt chapter files")
    parser.add_argument("--book", help="eval book whose expected files score matching chapters")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    load_dotenv(SCRIPT_DIR / ".env.local")
    logging.basicConfig(level=logging.WARNING)
    collector = collect_usage()

    book = Book.load(BOOKS_DIR / args.book) if args.book else None
    args.out.mkdir(parents=True, exist_ok=True)
    cast, voices, rows = Cast(), fake_voices(), []
    for path in sorted(args.chapters.glob("[0-9]*.txt")):
        text = path.read_text(encoding="utf-8")
        collector.calls.clear()
        started = time.monotonic()
        script, cast = build_script(text, cast, voices)
        row = {
            "chapter": path.stem,
            "seconds": time.monotonic() - started,
            "cost": collector.cost() or 0.0,
            "words": len(text.split()),
            "cast_size": len(cast.members),
            **review_counts(script, text),
        }
        expected = BOOKS_DIR / args.book / f"{path.stem}-expected.txt" if book else None
        if book and expected and expected.exists():
            row["score"] = score(book, script, cast, text, expected)
        rows.append(row)
        (args.out / f"{path.stem}-script.txt").write_text(render(script, cast, text), encoding="utf-8")
        (args.out / "cast.json").write_text(cast.model_dump_json(indent=2), encoding="utf-8")
        print(summary_line(row), flush=True)

    (args.out / "report.md").write_text(report(rows, cast), encoding="utf-8")
    print(f"\nReport: {args.out / 'report.md'}")


def review_counts(script: Script, text: str) -> dict:
    dialogue = dialogue_lines(script, text)
    flagged = [s for s in dialogue if (s.confidence or 0) < REVIEW_BELOW]
    return {"segments": len(script.segments), "dialogue": len(dialogue), "flagged": len(flagged)}


def dialogue_lines(script: Script, text: str):
    """Lines a character speaks or the splitter marked as speech. Narration the
    narrator reads isn't worth reviewing; speech given to the narrator is."""
    segments = get_text_segments(text)
    if len(segments) == len(script.segments):
        return [s for s, t in zip(script.segments, segments) if t.is_dialogue]
    return [s for s in script.segments if s.speaker_id != NARRATOR_ID]


def score(book: Book, script: Script, cast: Cast, text: str, expected_path: Path) -> dict:
    labels = score_labels(book, script, cast, get_text_segments(text), load_expected(expected_path))
    wrong = [c for c, right in labels["confidences"] if not right]
    return {
        "correct": labels["dialogue_correct"],
        "total": labels["dialogue_total"],
        "mistakes": len(labels["mistakes"]),
        "mistakes_flagged": sum(c < REVIEW_BELOW for c in wrong),
    }


def render(script: Script, cast: Cast, text: str) -> str:
    dialogue = {s.id for s in dialogue_lines(script, text)}
    lines = []
    for s in script.segments:
        member = cast.get(s.speaker_id)
        name = member.names[0] if member else s.speaker_id
        if s.id in dialogue:
            flag = " REVIEW" if (s.confidence or 0) < REVIEW_BELOW else ""
            lines.append(f"{name} ({s.confidence or 0:.2f}){flag}: {s.text}")
        else:
            lines.append(f"{name}: {s.text}")
    return "\n".join(lines) + "\n"


def summary_line(row: dict) -> str:
    scored = ""
    if "score" in row:
        s = row["score"]
        scored = f", {s['correct']}/{s['total']} right, {s['mistakes_flagged']}/{s['mistakes']} mistakes flagged"
    return (
        f"ch{row['chapter']}: {row['words']} words, {row['dialogue']} dialogue lines, "
        f"{row['flagged']} flagged, cast {row['cast_size']}, ${row['cost']:.4f}, {row['seconds']:.0f}s{scored}"
    )


def report(rows: list[dict], cast: Cast) -> str:
    members = [m for m in cast.members if m.id != NARRATOR_ID]
    dialogue = sum(r["dialogue"] for r in rows)
    flagged = sum(r["flagged"] for r in rows)
    out = [
        "# Whole-book run",
        "",
        f"- Chapters: {len(rows)}, words: {sum(r['words'] for r in rows)}",
        f"- Cost: ${sum(r['cost'] for r in rows):.4f}, time: {sum(r['seconds'] for r in rows) / 60:.1f} min "
        f"(median chapter {statistics.median(r['seconds'] for r in rows):.0f}s)",
        f"- Dialogue lines: {dialogue}; flagged for review (confidence < {REVIEW_BELOW}): "
        f"{flagged} ({flagged / dialogue:.0%})" if dialogue else "- No dialogue",
        f"- Characters: {len(members)}; without a voice: {sum(m.voice is None for m in members)}",
        "",
        "| Chapter | Words | Dialogue | Flagged | Cast | Cost | Seconds | Scored |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        s = r.get("score")
        scored = f"{s['correct']}/{s['total']}, {s['mistakes_flagged']}/{s['mistakes']} mistakes flagged" if s else ""
        out.append(
            f"| {r['chapter']} | {r['words']} | {r['dialogue']} | {r['flagged']} | {r['cast_size']} "
            f"| ${r['cost']:.4f} | {r['seconds']:.0f} | {scored} |"
        )
    out += ["", "## Cast", "", "| id | names | age | gender | voice |", "|---|---|---|---|---|"]
    out += [f"| {m.id} | {', '.join(m.names)} | {m.age} | {m.gender} | {m.voice} |" for m in cast.members]
    overlaps = [
        (a, b)
        for i, a in enumerate(members)
        for b in members[i + 1 :]
        if any(names_overlap(x, y) for x in a.names for y in b.names)
    ]
    if overlaps:
        out += ["", "## Possible duplicates (names overlap)", ""]
        out += [f"- {a.id} {a.names} / {b.id} {b.names}" for a, b in overlaps]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()
