# Text to Audiobook

An experiment: turn a book's text into a multi-voice audiobook script, where
every line of dialogue is read by its character's voice.

It is split into two steps with a person checking the script in between:

1. **Script** (`script/`): find the characters in a chapter, then label who
   speaks every line. This is the hard part and where the work is focused.
2. **Narration** (`narration/`): read a checked script aloud, cloning each
   character's voice from a short recording, with Qwen3-TTS.

Each step is a stateless RunPod serverless worker: a job's input carries
everything it needs and the caller saves what comes back. A separate app
(mobile or web) holds the books, scripts, voices and audio, and is where a
person checks the script.

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
.venv/bin/python -m tta_script build ../books/<name>   # writes scripts/*.json and cast.json; about 3s a chapter
```

## Narration

```sh
cd narration
make install    # on a Mac: runs Qwen3-TTS through MLX
make lint types test
```

`tta_narration.narrate.narrate(script, cast, voices, model)` reads a checked
chapter aloud and times every line. Every character with lines needs a voice,
and every voice a clip with its exact transcript. On a Mac M1 Pro it runs about
as fast as the speech it makes; first run downloads the model (about 2 GB).

Speech models are swappable. Each one subclasses `SpeechModel` in
`narration/tta_narration/speech.py` (a `sample_rate` and
`say(texts, voice) -> audio per text`), lives in `tta_narration/models/`, and is
listed by name in `MODELS`. `TTA_SPEECH_MODEL` picks one; the default is
`qwen3-tts` on a GPU and `qwen3-tts-mlx` on a Mac.

## Workers

Both run on [RunPod serverless](https://docs.runpod.io/serverless/overview),
which queues jobs, runs them in the background and scales to zero. The job
formats are in each worker's docstring: `script/tta_script/worker.py`
(`build`, `recheck`) and `narration/tta_narration/worker.py`.

| Worker | Hardware | Image | Endpoint settings |
|---|---|---|---|
| script | CPU | `cd script && make image` | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` |
| narration | NVIDIA GPU, 24 GB | `cd narration && make image` | none |

Push each image to a registry RunPod can pull from and create an endpoint from
it. To try a job locally first: `make worker JOB=job.json` in either folder,
with the job as `{"input": {...}}`.

The narration image runs Qwen3-TTS through PyTorch, which has not yet been run
on a GPU; the Mac path (MLX) is the one tested.
