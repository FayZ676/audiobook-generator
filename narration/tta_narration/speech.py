"""The contract every speech model meets, and choosing one by name.

To add a model: subclass SpeechModel in tta_narration/models/, implementing
sample_rate and say, and add it to MODELS. Nothing else changes: narration
only ever talks to a SpeechModel.
"""

import importlib
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class VoiceClip:
    """A voice to clone: a recording of it and exactly what is said in it."""

    path: str  # a WAV file
    transcript: str


class SpeechModel(ABC):
    """A text-to-speech model that reads text in a voice cloned from a clip.

    Loading happens in __init__, once per worker, so it may be slow; say is
    called many times after."""

    # How many texts say reads at once at its best speed. Narration hands it
    # about this many at a time, from as many lines as it takes; a model that
    # reads one at a time keeps 1, so each line comes as soon as it is read.
    batch_size: int = 1

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """The sample rate of the audio say returns."""

    @abstractmethod
    def say(self, texts: list[str], voice: VoiceClip) -> list[np.ndarray]:
        """Each text read in voice: one float32 mono array per text, in the
        same order, at sample_rate.

        Texts are at most about 40 words, with straight quotes: the pieces of
        the next few lines of the script that share a voice, about batch_size
        of them, in the order a listener hears them. Calls keep coming in a
        few voices, so a model should prepare each voice once and reuse it."""


# name -> "module:class", imported only when chosen, since each model needs
# libraries the others don't (PyTorch with CUDA, MLX on a Mac).
MODELS = {
    "qwen3-tts": "tta_narration.models.qwen:QwenTorch",
    "qwen3-tts-mlx": "tta_narration.models.qwen:QwenMlx",
}
DEFAULT_MODEL = "qwen3-tts-mlx" if sys.platform == "darwin" else "qwen3-tts"


def load_speech_model(name: str | None = None) -> SpeechModel:
    """The named model (default: TTA_SPEECH_MODEL, else the one for this
    machine), loaded and ready."""
    name = name or os.environ.get("TTA_SPEECH_MODEL") or DEFAULT_MODEL
    if name not in MODELS:
        raise ValueError(f"No speech model {name!r}; there are {', '.join(MODELS)}")
    module, cls = MODELS[name].split(":")
    model = getattr(importlib.import_module(module), cls)()
    if not isinstance(model, SpeechModel):
        raise TypeError(f"{MODELS[name]} is not a SpeechModel")
    return model
