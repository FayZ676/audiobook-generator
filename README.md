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

## Narration

```sh
cd f5
make install    # downloads the F5-TTS checkpoint and vocoder
```
