import io
import re
from importlib.resources import files
from pathlib import Path
from typing import Optional, Dict, Tuple, Any

import librosa
import numpy as np
import soundfile as sf
from cached_path import cached_path
from hydra.utils import get_class
from omegaconf import OmegaConf, DictConfig

from f5_tts.infer.utils_infer import (
    infer_process,
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
)

from tta_speech.types import InferenceParams


def _initialize_inference(
    output_path: str,
    model_name: str,
    model_cfg_path: Optional[str],
    ckpt_file: Optional[str],
    vocab_file: str,
    vocoder_name: str,
    load_vocoder_from_local: bool,
    vocoder_local_path: str,
    device: str,
) -> Tuple[Any, Any, DictConfig, Path, str]:
    """Initializes paths, loads vocoder and TTS model."""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    vocoder = load_vocoder(
        vocoder_name=vocoder_name,
        is_local=load_vocoder_from_local,
        local_path=vocoder_local_path,
        device=device,
    )

    if not model_cfg_path:
        try:
            model_cfg_path = str(files("f5_tts").joinpath(f"configs/{model_name}.yaml"))
        except ModuleNotFoundError as e:
            _base_path = Path(__file__).parent.parent
            model_cfg_path_rel = _base_path / f"configs/{model_name}.yaml"
            if not model_cfg_path_rel.exists():
                model_cfg_path_rel = _base_path.parent / f"configs/{model_name}.yaml"
                if not model_cfg_path_rel.exists():
                    raise FileNotFoundError(
                        f"Default config for {model_name} not found via package resources or relative paths."
                    ) from e
            model_cfg_path = str(model_cfg_path_rel)

    model_cfg = OmegaConf.load(model_cfg_path)
    model_cls = get_class(f"f5_tts.model.{model_cfg.model.backbone}")
    model_arc = model_cfg.model.arch

    if not ckpt_file:
        repo_name, ckpt_step, ckpt_type = "F5-TTS", 1250000, "safetensors"
        ckpt_file_url = (
            f"hf://SWivid/{repo_name}/{model_name}/model_{ckpt_step}.{ckpt_type}"
        )
        try:
            ckpt_file = str(cached_path(ckpt_file_url))
        except Exception as e:
            raise ConnectionError(
                f"Failed to download checkpoint from {ckpt_file_url}. Please check the URL or provide a local path."
            ) from e

    ema_model = load_model(
        model_cls,
        model_arc,
        ckpt_file,
        mel_spec_type=vocoder_name,
        vocab_file=vocab_file,
        device=device,
    )
    return ema_model, vocoder, model_cfg, output_dir, device


def _prepare_voices(
    ref_audio: str, ref_text: str, voices: Optional[Dict[str, Dict[str, str]]]
) -> Dict[str, Dict[str, Any]]:
    """Prepares and preprocesses the main and additional voices."""
    all_voices = {}
    if voices:
        all_voices.update(voices)

    all_voices["main"] = {"ref_audio": ref_audio, "ref_text": ref_text}

    processed_voices = {}
    for voice_name, voice_data in all_voices.items():
        try:
            processed_audio, processed_text = preprocess_ref_audio_text(
                voice_data["ref_audio"], voice_data["ref_text"]
            )
            processed_voices[voice_name] = {
                "ref_audio": processed_audio,
                "ref_text": processed_text,
            }
        except Exception as e:
            print(f"Error processing reference for voice '{voice_name}': {e}")
            print(f"    Skipping voice '{voice_name}'.")

    if "main" not in processed_voices:
        raise ValueError("Main reference audio could not be processed or was invalid.")

    return processed_voices


def _synthesize_text_chunks(
    gen_text: str,
    prepared_voices: Dict[str, Dict[str, Any]],
    ema_model: Any,
    vocoder: Any,
    vocoder_name: str,
    infer_params: InferenceParams,
    device: str,
    save_chunk: bool,
    output_dir: Path,
    output_file_name: str,
) -> Tuple[list[np.ndarray], Optional[int]]:
    """Synthesizes audio chunk by chunk based on voice tags."""
    generated_audio_segments = []
    final_sample_rate = None

    reg_split = r"(?=\[\w+\])"
    reg_extract = r"\[(\w+)\]"

    chunks = re.split(reg_split, gen_text)

    output_chunk_dir = None
    if save_chunk:
        output_chunk_dir = output_dir / f"{Path(output_file_name).stem}_chunks"
        output_chunk_dir.mkdir(parents=True, exist_ok=True)

    for i, text_chunk in enumerate(chunks):
        if not text_chunk.strip():
            continue

        match = re.match(reg_extract, text_chunk)
        current_voice_name = "main"
        if match:
            extracted_voice = match.group(1)
            if extracted_voice in prepared_voices:
                current_voice_name = extracted_voice
            else:
                # Consider adding logging here instead of print
                print(
                    f"Warning: Voice tag '[{extracted_voice}]' not found in provided voices. Using 'main'."
                )
            text_to_synthesize = re.sub(reg_extract, "", text_chunk).strip()
        else:
            text_to_synthesize = text_chunk.strip()

        if not text_to_synthesize:
            continue

        current_ref_audio = prepared_voices[current_voice_name]["ref_audio"]
        current_ref_text = prepared_voices[current_voice_name]["ref_text"]
        try:
            audio_segment, sr, _ = infer_process(
                current_ref_audio,
                current_ref_text,
                text_to_synthesize,
                ema_model,
                vocoder,
                mel_spec_type=vocoder_name,
                target_rms=infer_params.target_rms,
                cross_fade_duration=infer_params.cross_fade_duration,
                nfe_step=infer_params.nfe_step,
                cfg_strength=infer_params.cfg_strength,
                sway_sampling_coef=infer_params.sway_sampling_coef,
                speed=infer_params.speed,
                fix_duration=infer_params.fix_duration,
                device=device,
            )
            generated_audio_segments.append(audio_segment)
            if final_sample_rate is None:
                final_sample_rate = sr

            if save_chunk and output_chunk_dir:
                chunk_filename = f"{i}_{text_to_synthesize[:30].replace(' ', '_')}.wav"
                chunk_path = output_chunk_dir / chunk_filename
                sf.write(str(chunk_path), audio_segment, sr)

        except Exception as e:
            raise RuntimeError(
                f"Error during inference for voice '{current_voice_name}' with text '{text_to_synthesize}': {e}"
            ) from e

    return generated_audio_segments, final_sample_rate


def _postprocess_and_encode(
    audio_segments: list[np.ndarray],
    sample_rate: int,
    remove_silence: bool,
    silence_top_db: int,
) -> bytes:
    """Concatenates audio segments, optionally removes silence, and encodes to WAV bytes."""
    if not audio_segments:
        return b""

    final_wave = np.concatenate(audio_segments)
    if remove_silence:
        try:
            trimmed_wave, _ = librosa.effects.trim(final_wave, top_db=silence_top_db)
            if len(trimmed_wave) < len(final_wave):
                final_wave = trimmed_wave
        except Exception as e:
            # Consider logging the error instead of printing
            print(f"Warning: Failed to remove silence: {e}")

    bytes_wav = io.BytesIO()
    try:
        sf.write(bytes_wav, final_wave, sample_rate, format="WAV", subtype="PCM_16")
        return bytes_wav.getvalue()
    except Exception as e:
        # Consider logging the error instead of printing
        print(f"Error writing final WAV: {e}")
        return b""


def infer(params: InferenceParams) -> tuple[bytes, int | None]:
    ema_model, vocoder, model_cfg, output_dir, device = _initialize_inference(
        output_path=params.output_path,
        model_name=params.model_name,
        model_cfg_path=params.model_cfg_path,
        ckpt_file=params.ckpt_file,
        vocab_file=params.vocab_file,
        vocoder_name=params.vocoder_name,
        load_vocoder_from_local=params.load_vocoder_from_local,
        vocoder_local_path=params.vocoder_local_path,
        device=params.device,
    )

    prepared_voices = _prepare_voices(params.ref_audio, params.ref_text, params.voices)
    output_file_name = Path(params.output_path).name

    generated_audio_segments, final_sample_rate = _synthesize_text_chunks(
        gen_text=params.gen_text,
        prepared_voices=prepared_voices,
        ema_model=ema_model,
        vocoder=vocoder,
        vocoder_name=params.vocoder_name,
        infer_params=params,
        device=device,
        save_chunk=params.save_chunk,
        output_dir=output_dir,
        output_file_name=output_file_name,
    )

    if not generated_audio_segments or final_sample_rate is None:
        return b"", final_sample_rate

    wav_data = _postprocess_and_encode(
        audio_segments=generated_audio_segments,
        sample_rate=final_sample_rate,
        remove_silence=params.remove_silence,
        silence_top_db=params.silence_top_db,
    )

    return wav_data, final_sample_rate
