"""Build a book's scripts for the editor to open.

A book is a folder holding chapters/*.txt, one file per chapter, named so
they sort in reading order (01.txt, 02.txt, ...). Chapters are built in that
order, each with the cast so far, and written as:

- scripts/<chapter>.json: the chapter's script
- cast.json: everyone found so far, updated after each chapter

A chapter that already has a script is skipped, so rerunning after adding
chapters builds only the new ones and never overwrites a reviewed script.

    .venv/bin/python -m tta_script ../books/alice
    .venv/bin/python -m tta_script ../books/alice --voices voices.json
"""

import argparse
import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from tta_script.cast import Cast, Voice
from tta_script.pipeline import build_script


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", maxsplit=1)[0])
    parser.add_argument("book", type=Path, help="book folder with a chapters/ folder of .txt files")
    parser.add_argument("--voices", type=Path, help="JSON list of voices to give characters (default: none)")
    args = parser.parse_args()

    load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")
    logging.basicConfig(level=logging.WARNING)
    chapters = sorted((args.book / "chapters").glob("*.txt"))
    if not chapters:
        parser.error(f"no chapters in {args.book / 'chapters'}")
    voices = [Voice.model_validate(v) for v in json.loads(args.voices.read_text())] if args.voices else []

    cast_file, scripts = args.book / "cast.json", args.book / "scripts"
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


if __name__ == "__main__":
    main()
