import numpy as np
from pathlib import Path
from importlib.resources import files
from dataclasses import dataclass

from hydra.utils import get_class
from omegaconf import OmegaConf

from f5_tts.infer.utils_infer import (
    infer_process,
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
)
from f5_tts.infer.utils_infer import (
    target_rms as default_target_rms,
    cross_fade_duration as default_cross_fade_duration,
    nfe_step as default_nfe_step,
    cfg_strength as default_cfg_strength,
    sway_sampling_coef as default_sway_sampling_coef,
    speed as default_speed,
    fix_duration as default_fix_duration,
    device as default_device,
)

from tta_types.interfaces import SpeechGeneratorInterface
from tta_types.types import SpeechRequestSegment, Voice


VoiceName = str


@dataclass
class PreparedVoice:
    ref_audio: str
    ref_text: str


class F5Client(SpeechGeneratorInterface):
    def __init__(self, voices: set[Voice]) -> None:
        self._vocoder_path = f"{Path(__file__).parent}/vocos"
        self._model_config = OmegaConf.load(
            str(files("f5_tts").joinpath("configs/F5TTS_v1_Base.yaml"))
        )
        self.device = default_device
        self.vocoder_name = "vocos"
        self.vocoder = load_vocoder(
            vocoder_name=self.vocoder_name,
            is_local=True,
            local_path=self._vocoder_path,
            device=self.device,
        )
        self.model = load_model(
            model_cls=get_class(f"f5_tts.model.{self._model_config.model.backbone}"),
            model_cfg=self._model_config.model.arch,
            mel_spec_type=self.vocoder_name,
            ckpt_path=f"{Path(__file__).parent}/checkpoints/model_1250000.safetensors",
            vocab_file=f"{Path(__file__).parent}/vocab.txt",
            device=self.device,
        )
        self.voices = self._prepare_voices(voices=voices)

    def generate(self, segments: list[SpeechRequestSegment]):
        """Synthesizes audio chunk by chunk based on voice tags."""
        generated_audio_segments: list[np.ndarray] = []
        # TODO: Why do we need this?
        final_sample_rate = None

        for segment in segments:
            if not segment.text.strip():
                continue

            current_ref_audio = self.voices[segment.voice_name].ref_audio
            current_ref_text = self.voices[segment.voice_name].ref_text
            audio_segment, sample_rate, _ = infer_process(  # type: ignore
                current_ref_audio,
                current_ref_text,
                segment.text,
                model_obj=self.model,
                vocoder=self.vocoder,
                mel_spec_type=self.vocoder_name,
                target_rms=default_target_rms,
                cross_fade_duration=default_cross_fade_duration,
                nfe_step=default_nfe_step,
                cfg_strength=default_cfg_strength,
                sway_sampling_coef=default_sway_sampling_coef,
                speed=default_speed,
                fix_duration=default_fix_duration,
                device=self.device,
            )

            if not isinstance(audio_segment, np.ndarray):
                raise ValueError("Invalid audio segment generated.")

            generated_audio_segments.append(audio_segment)
            final_sample_rate = final_sample_rate or sample_rate
            generated_audio_segments.append(_create_silence(sample_rate, 0.75))

        return generated_audio_segments, final_sample_rate

    @staticmethod
    def _prepare_voices(voices: set[Voice]) -> dict[VoiceName, PreparedVoice]:
        processed_voices: dict[VoiceName, PreparedVoice] = dict()
        for v in voices:
            processed_audio, processed_text = preprocess_ref_audio_text(
                ref_audio_orig=v.audio_path, ref_text=v.audio_transcript
            )
            processed_voices[v.name] = PreparedVoice(
                ref_audio=processed_audio, ref_text=processed_text
            )
        return processed_voices


def _create_silence(sample_rate: int, duration_seconds: float) -> np.ndarray:
    """Creates a numpy array of silence for the specified duration."""
    num_samples = int(sample_rate * duration_seconds)
    return np.zeros(num_samples, dtype=np.float32)
