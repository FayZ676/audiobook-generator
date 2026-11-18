# Text to Audiobook

An experiment: turn a book's text into a multi-voice audiobook script, where
every line of dialogue is read by its character's voice.

It is split into two steps with a person checking the script in between:

1. **Script** (`script/`): find the characters in a chapter, then label who
   speaks every line. This is the hard part and where the work is focused.
2. **Narration** (`narration/`): read a checked script aloud, each character
   in one of Kokoro's preset voices.

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
brew install espeak-ng   # Kokoro spells out unknown words with it
make install    # on a Mac: runs Kokoro through MLX
make lint types test
```

`tta_narration.narrate.narrate(script, cast, model)` reads a checked script
aloud a line at a time, in order, yielding each line as it is read so
playback can start with the first. The worker sends each line as an MP3 of
its own (see `narration/tta_narration/worker.py` for the chunk format). Every
character with lines needs a voice: the name of one of the model's voices,
such as `bm_lewis` (Kokoro's are listed in `tta_narration/models/kokoro.py`).
On a Mac M1 Pro, Kokoro reads about 17 times faster than real time.

Speech models are swappable. Each one subclasses `SpeechModel` in
`narration/tta_narration/speech.py` (a `sample_rate`, its `voices`, and
`say(texts, voice) -> audio per text`), lives in `tta_narration/models/`, and is
listed by name in `MODELS`. `TTA_SPEECH_MODEL` picks one; the default is
`kokoro` (PyTorch) on a GPU and `kokoro-mlx` on a Mac.

## Deploying

Both steps run as [RunPod serverless](https://docs.runpod.io/serverless/overview)
workers, which queue jobs, run them in the background and scale to zero. The
job formats are in each worker's docstring: `script/tta_script/worker.py`
(`build`, `recheck`) and `narration/tta_narration/worker.py`.

Everything RunPod runs is in [`deploy/runpod.toml`](deploy/runpod.toml): each
endpoint's image, CPU or GPU, workers, scaling, timeout and environment, and
the secrets they read. Nothing is set up in the console.

1. Push to main. GitHub Actions builds each image whose code changed and
   pushes it to GHCR, tagged with the last commit that touched it
   (`gh run watch` to follow it).
2. `make plan` shows what differs between RunPod and `runpod.toml`.
3. `make apply` makes RunPod match: creates or updates the secrets and
   endpoints. A new image rolls out as workers finish their jobs.

```sh
make status                                         # jobs, workers, rollouts
python3 -m deploy run tta-script job.json           # job.json: {"input": {...}}
python3 -m deploy run tta-narration job.json --stream   # each chunk as it comes
python3 -m deploy logs tta-narration --follow
python3 -m deploy destroy tta-script                # asks first
```

`.env.local` at the repo root holds `RUNPOD_API_KEY` (an API key from
RunPod's settings) and the secret values `runpod.toml` lists
(`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`). `apply` copies them into RunPod
secrets, and again whenever one changes.

The images are public on GHCR, as the repository is, so RunPod pulls them
without a registry login. `make plan` checks each one can be pulled.

The narration image runs Kokoro through PyTorch, which has not yet been run
on a GPU; the Mac path (MLX) is the one tested.

`make test-deploy` checks the deploy tool itself.
