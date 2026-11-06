# Text to Audiobook

An experiment: turn a book's text into a multi-voice audiobook script, where
every line of dialogue is read by its character's voice.

It is split into two steps with a person checking the script in between:

1. **Script** (`script/`): find the characters in a chapter, then label who
   speaks every line. This is the hard part and where the work is focused.
2. **Narration** (`f5/`): read a checked script aloud with F5-TTS voices.

## Script

```sh
cd script
make install                  # needs Python 3.12
cp .env.example .env.local    # add ANTHROPIC_API_KEY and OPENAI_API_KEY
make lint types test          # offline checks, no API calls
.venv/bin/python -m evals.dialogue_accuracy --runs 5   # scores the models on hand-labelled chapters (paid, ~1 cent a run)
```

`tta_script.pipeline.build_script(text, cast, voices)` is the entry point: a
chapter's text and the book's cast so far in, the labelled script and updated
cast out. Run chapters in order.

To build a whole book, put its chapters in `books/<name>/chapters/` (one
`.txt` per chapter, named to sort in reading order; `books/` is git-ignored)
and run:

```sh
.venv/bin/python -m tta_script ../books/<name>   # writes scripts/*.json and cast.json; about 3s a chapter
```

## Editor

Where a person checks the script (`editor/`, Next.js). It reads and writes
`books/` directly.

```sh
cd editor
npm install
npm run dev     # http://localhost:3000
```

- **Overview**: what is left before the book is ready to narrate.
- **Fix lines**: the lines the model was least sure of, 25 at a time. Confirm one
  (Enter) or pick the speaker (1-9, or / to search or add a character); Z
  undoes. Once 20 lines in a row need no fix, the rest are very likely right
  and the book shows as ready to narrate.
- **Cast**: names, age and gender for everyone, most lines first. Characters
  the voice library had no match for show "No voice".
- **Read**: a chapter as a script; click any line to change its speaker.

## Narration

```sh
cd f5
make install    # downloads the F5-TTS checkpoint and vocoder
```
