"""Qwen3-TTS 1.7B, which clones a voice from a clip and its transcript.

On an NVIDIA GPU (RunPod) it runs through PyTorch; on a Mac, through MLX, so
narration can be tried locally without a GPU. Both read the same way."""

import numpy as np

from tta_narration.speech import SpeechModel, VoiceClip

LANGUAGE = "english"


class QwenTorch(SpeechModel):
    MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
    BATCH = 8  # pieces read at once; not yet tuned on a real GPU
    sample_rate = 24000

    def __init__(self) -> None:
        # Only on the GPU image, so not importable on a Mac.
        import torch  # type: ignore  # pylint: disable=import-outside-toplevel,import-error
        from qwen_tts import Qwen3TTSModel  # type: ignore  # pylint: disable=import-outside-toplevel,import-error

        self._model = Qwen3TTSModel.from_pretrained(self.MODEL, device_map="cuda:0", dtype=torch.bfloat16)
        self._prompts: dict[VoiceClip, list] = {}

    def say(self, texts: list[str], voice: VoiceClip) -> list[np.ndarray]:
        if voice not in self._prompts:
            self._prompts[voice] = self._model.create_voice_clone_prompt(ref_audio=voice.path, ref_text=voice.transcript)
        prompt = self._prompts[voice]
        out: list[np.ndarray] = []
        for i in range(0, len(texts), self.BATCH):
            batch = texts[i : i + self.BATCH]
            wavs, sample_rate = self._model.generate_voice_clone(
                text=batch, language=[LANGUAGE] * len(batch), voice_clone_prompt=prompt * len(batch)
            )
            if sample_rate != self.sample_rate:
                raise RuntimeError(f"{self.MODEL} returned {sample_rate} Hz audio, not {self.sample_rate}")
            out.extend(np.asarray(w, dtype=np.float32).reshape(-1) for w in wavs)
        return out


class QwenMlx(SpeechModel):
    MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"

    def __init__(self) -> None:
        from mlx_audio.tts.utils import load_model  # type: ignore  # pylint: disable=import-outside-toplevel

        self._model = load_model(model_path=self.MODEL)

    @property
    def sample_rate(self) -> int:
        return self._model.sample_rate

    def say(self, texts: list[str], voice: VoiceClip) -> list[np.ndarray]:
        import mlx.core as mx  # type: ignore  # pylint: disable=import-outside-toplevel

        out: list[np.ndarray] = []
        for text in texts:
            results = self._model.generate(text, ref_audio=voice.path, ref_text=voice.transcript, lang_code=LANGUAGE)
            out.append(np.concatenate([np.asarray(r.audio, dtype=np.float32).reshape(-1) for r in results]))
            mx.clear_cache()
        return out
