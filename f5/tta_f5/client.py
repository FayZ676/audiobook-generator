import tempfile
import numpy as np
from pathlib import Path
from importlib.resources import files
from dataclasses import dataclass

import soundfile as sf
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

from tta_types.interfaces import (
    SpeechGeneratorInterface,
    VoiceName,
    SegmentId,
    SpeechAudioPath,
)
from tta_types.types import SpeechRequestSegment, Voice

from tta_f5.utils import create_silence


@dataclass
class PreparedVoice:
    ref_audio: str
    ref_text: str


SpeechResult = np.ndarray


class F5Client(SpeechGeneratorInterface[PreparedVoice, SpeechResult]):
    def __init__(self, voices: list[Voice]) -> None:
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
        processed_segments_paths: dict[SegmentId, SpeechAudioPath] = {}

        for segment in segments:
            audio_segment, sample_rate, _ = infer_process(  # type: ignore
                ref_audio=self.voices[segment.voice_name].ref_audio,
                ref_text=self.voices[segment.voice_name].ref_text,
                gen_text=segment.text,
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

            processed_segments_paths[segment.id] = self._save_result(
                np.concatenate([audio_segment, create_silence(sample_rate, 0.75)]),
                sample_rate,
            )

        return processed_segments_paths

    @staticmethod
    def _prepare_voices(voices: list[Voice]) -> dict[VoiceName, PreparedVoice]:
        processed_voices: dict[VoiceName, PreparedVoice] = dict()
        for v in voices:
            processed_audio, processed_text = preprocess_ref_audio_text(
                ref_audio_orig=v.audio_path, ref_text=v.audio_transcript
            )
            processed_voices[v.name] = PreparedVoice(
                ref_audio=processed_audio, ref_text=processed_text
            )
        return processed_voices

    @staticmethod
    def _save_result(result: SpeechResult, sample_rate: int) -> str:
        """Save audio numpy array to a temporary WAV file and return the file path."""
        with tempfile.NamedTemporaryFile(
            suffix=".wav", dir="/tmp", delete=False
        ) as temp_file:
            temp_path = temp_file.name
        sf.write(temp_path, result, sample_rate, format="WAV", subtype="PCM_16")
        return temp_path
