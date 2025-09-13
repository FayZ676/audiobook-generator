from dataclasses import dataclass
from typing import Optional

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


@dataclass
class InferenceParams:
    gen_text: str
    voices: dict[str, dict[str, str]]
    load_vocoder_from_local: bool
    ref_audio: str | None = None
    ref_text: str | None = None
    model_name: str = "F5TTS_v1_Base"
    target_rms: float = default_target_rms
    cross_fade_duration: float = default_cross_fade_duration
    nfe_step: int = default_nfe_step
    cfg_strength: float = default_cfg_strength
    sway_sampling_coef: float = default_sway_sampling_coef
    speed: float = default_speed
    fix_duration: float | None = default_fix_duration
    device: str = default_device
    remove_silence: bool = False
    save_chunk: bool = False
    silence_top_db: int = 60


@dataclass(frozen=True, eq=True)
class InputData:
    text: str
    voices: dict[str, dict[str, str]]
