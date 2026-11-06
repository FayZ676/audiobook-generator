"""Build a book's scripts for the editor, and get a stronger model's opinion
on lines when the editor asks.

A book is a folder holding chapters/*.txt, one file per chapter, named so
they sort in reading order (01.txt, 02.txt, ...).

build: builds each chapter in that order, with the cast so far, writing
scripts/<chapter>.json and cast.json (updated after each chapter). A chapter
that already has a script is skipped, so rerunning after adding chapters
builds only the new ones and never overwrites a reviewed script.

recheck: asks the stronger model who speaks the given lines of one chapter
(segment ids), or, with none given, every dialogue line not yet reviewed.
Prints {segment id: speaker id} as JSON; the editor saves it.

    .venv/bin/python -m tta_script build ../books/alice
    .venv/bin/python -m tta_script build ../books/alice --voices voices.json
    .venv/bin/python -m tta_script recheck ../books/alice 07 seg-0012 seg-0040
"""

import argparse
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from tta_script.cast import Cast, Voice
from tta_script.dialogue.recheck import recheck_lines
from tta_script.pipeline import build_script
from tta_script.script import Script


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="build every chapter that has no script yet")
    build.add_argument("book", type=Path, help="book folder with a chapters/ folder of .txt files")
    build.add_argument("--voices", type=Path, help="JSON list of voices to give characters (default: none)")
    recheck = commands.add_parser("recheck", help="print a stronger model's speakers for lines of a chapter")
    recheck.add_argument("book", type=Path)
    recheck.add_argument("chapter", help="chapter name, as in scripts/<chapter>.json")
    recheck.add_argument("segments", nargs="*", help="segment ids (default: every unreviewed dialogue line)")
    args = parser.parse_args()

    load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")
    logging.basicConfig(level=logging.WARNING)
    if args.command == "build":
        build_book(args.book, args.voices, parser)
    else:
        print(json.dumps(recheck_chapter(args.book, args.chapter, args.segments)))


def build_book(book: Path, voices_file: Path | None, parser: argparse.ArgumentParser):
    chapters = sorted((book / "chapters").glob("*.txt"))
    if not chapters:
        parser.error(f"no chapters in {book / 'chapters'}")
    voices = [Voice.model_validate(v) for v in json.loads(voices_file.read_text())] if voices_file else []

    cast_file, scripts = book / "cast.json", book / "scripts"
    cast = Cast.model_validate_json(cast_file.read_text()) if cast_file.exists() else Cast()
    scripts.mkdir(exist_ok=True)
    for chapter in chapters:
        out = scripts / f"{chapter.stem}.json"
        if out.exists():
            continue
        script, cast = build_script(chapter.read_text(encoding="utf-8"), cast, voices)
        out.write_text(script.model_dump_json(indent=1), encoding="utf-8")
        cast_file.write_text(cast.model_dump_json(indent=2), encoding="utf-8")
        print(f"{chapter.stem}: {len(script.segments)} segments, cast {len(cast.members)}", flush=True)


def recheck_chapter(book: Path, chapter: str, segment_ids: list[str]) -> dict[str, str]:
    script = Script.model_validate_json((book / "scripts" / f"{chapter}.json").read_text(encoding="utf-8"))
    cast = Cast.model_validate_json((book / "cast.json").read_text(encoding="utf-8"))
    index = {s.id: i for i, s in enumerate(script.segments)}
    if segment_ids:
        unknown = [s for s in segment_ids if s not in index]
        if unknown:
            raise SystemExit(f"No such segments in {chapter}: {', '.join(unknown)}")
        asked = [index[s] for s in segment_ids]
    else:
        asked = [i for i, s in enumerate(script.segments) if s.is_dialogue and not s.reviewed]
    # Lines asked about one or a few at a time come in quick succession, so
    # keep the chapter cached for them.
    answers = recheck_lines(script, cast, asked, cache=bool(segment_ids))
    return {script.segments[i].id: speaker for i, speaker in answers.items()}


if __name__ == "__main__":
    main()
