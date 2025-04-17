from dataclasses import dataclass
from typing import Optional

from f5_tts.infer.utils_infer import (
    mel_spec_type as default_mel_spec_type,
    target_rms as default_target_rms,
    cross_fade_duration as default_cross_fade_duration,
    nfe_step as default_nfe_step,
    cfg_strength as default_cfg_strength,
    sway_sampling_coef as default_sway_sampling_coef,
    speed as default_speed,
    fix_duration as default_fix_duration,
    device as default_device,
)


@dataclass
class InferenceParams:
    ref_audio: str
    ref_text: str
    gen_text: str
    output_path: str
    vocoder_name: str
    vocoder_local_path: str
    load_vocoder_from_local: bool
    vocab_file: str
    model_name: str = "F5TTS_v1_Base"
    model_cfg_path: Optional[str] = None
    ckpt_file: Optional[str] = None
    target_rms: float = default_target_rms
    cross_fade_duration: float = default_cross_fade_duration
    nfe_step: int = default_nfe_step
    cfg_strength: float = default_cfg_strength
    sway_sampling_coef: float = default_sway_sampling_coef
    speed: float = default_speed
    fix_duration: float | None = default_fix_duration
    device: str = default_device
    remove_silence: bool = False
    voices: Optional[dict[str, dict[str, str]]] = None
    save_chunk: bool = False
    silence_top_db: int = 60
