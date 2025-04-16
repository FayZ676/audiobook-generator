import io
import re
from importlib.resources import files
from pathlib import Path
from typing import Optional, Dict

import librosa
import numpy as np
import soundfile as sf
from cached_path import cached_path
from hydra.utils import get_class
from omegaconf import OmegaConf

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
    infer_process,
    load_model,
    load_vocoder,
    preprocess_ref_audio_text,
)


def infer(
    ref_audio: str,
    ref_text: str,
    gen_text: str,
    output_path: str,
    model_name: str = "F5TTS_v1_Base",
    model_cfg_path: Optional[str] = None,
    ckpt_file: Optional[str] = None,
    vocab_file: Optional[str] = None,
    vocoder_name: str = default_mel_spec_type,
    load_vocoder_from_local: bool = False,
    vocoder_local_path: Optional[str] = None,
    target_rms: float = default_target_rms,
    cross_fade_duration: float = default_cross_fade_duration,
    nfe_step: int = default_nfe_step,
    cfg_strength: float = default_cfg_strength,
    sway_sampling_coef: float = default_sway_sampling_coef,
    speed: float = default_speed,
    fix_duration: float = default_fix_duration,
    device: str = default_device,
    remove_silence: bool = False,
    voices: Optional[Dict[str, Dict[str, str]]] = None,
    save_chunk: bool = False,
    silence_top_db: int = 60,
) -> tuple[bytes, int | None]:
    output_dir = Path(output_path).parent
    output_file_name = Path(output_path).name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine default vocoder path if local loading is requested but path isn't specified
    if load_vocoder_from_local and not vocoder_local_path:
        if vocoder_name == "vocos":
            # Assuming a standard relative path structure
            vocoder_local_path = "../checkpoints/vocos-mel-24khz"
        elif vocoder_name == "bigvgan":
            vocoder_local_path = "../checkpoints/bigvgan_v2_24khz_100band_256x"
        else:
            # Fallback or raise error if vocoder name is unknown and path is needed
            print(
                f"Warning: Unknown vocoder '{vocoder_name}' specified for local loading without a path."
            )
            # Decide how to handle this: maybe default to non-local or raise an error
            load_vocoder_from_local = False  # Example: fallback to non-local

    # Load Vocoder
    vocoder = load_vocoder(
        vocoder_name=vocoder_name,
        is_local=load_vocoder_from_local,
        local_path=vocoder_local_path,
        device=device,
    )

    # Load TTS Model Config
    if not model_cfg_path:
        try:
            model_cfg_path = str(files("f5_tts").joinpath(f"configs/{model_name}.yaml"))
        except ModuleNotFoundError as e:
            # Handle case where package resources aren't available (e.g., running directly from repo)
            # This might require adjusting the path based on your project structure
            print(
                "Warning: Could not find default config via package resources. Trying relative path."
            )
            # Adjust this path as needed relative to where infer.py is located
            model_cfg_path = Path(__file__).parent.parent / f"configs/{model_name}.yaml"
            if not model_cfg_path.exists():
                raise FileNotFoundError(
                    f"Default config for {model_name} not found at {model_cfg_path}"
                ) from e
            model_cfg_path = str(model_cfg_path)

    model_cfg = OmegaConf.load(model_cfg_path)
    model_cls = get_class(f"f5_tts.model.{model_cfg.model.backbone}")
    model_arc = model_cfg.model.arch

    # Determine Checkpoint File
    if not ckpt_file:
        repo_name, ckpt_step, ckpt_type = "F5-TTS", 1250000, "safetensors"
        # Adjust defaults based on model name as in CLI
        if model_name == "F5TTS_Base":
            if vocoder_name == "vocos":
                ckpt_step = 1200000
            elif vocoder_name == "bigvgan":
                # Note: CLI logic changes model name here, which might be confusing.
                # Consider if the user should explicitly pass "F5TTS_Base_bigvgan" instead.
                # For now, mirroring CLI logic:
                # model_name = "F5TTS_Base_bigvgan" # This changes the input arg, maybe not ideal
                ckpt_type = "pt"
                print(
                    "Warning: Using F5TTS_Base with bigvgan requires specific checkpoint type (.pt)."
                )
        elif model_name == "E2TTS_Base":
            repo_name = "E2-TTS"
            ckpt_step = 1200000

        ckpt_file = str(
            cached_path(
                f"hf://SWivid/{repo_name}/{model_name}/model_{ckpt_step}.{ckpt_type}"
            )
        )
        print(f"Using default checkpoint: {ckpt_file}")

    # Load TTS Model
    print(f"Loading model {model_name} from {ckpt_file}...")
    ema_model = load_model(
        model_cls,
        model_arc,
        ckpt_file,
        mel_spec_type=vocoder_name,
        vocab_file=vocab_file,
        device=device,
    )
    print("Model loaded.")

    # Prepare voices dictionary
    all_voices = {}
    if voices:
        all_voices.update(voices)

    # Add the main voice provided via arguments
    all_voices["main"] = {"ref_audio": ref_audio, "ref_text": ref_text}

    # Preprocess all reference audios and texts
    print("Preprocessing reference audio(s)...")
    for voice_name, voice_data in all_voices.items():
        try:
            processed_audio, processed_text = preprocess_ref_audio_text(
                voice_data["ref_audio"], voice_data["ref_text"]
            )
            all_voices[voice_name]["ref_audio"] = processed_audio
            all_voices[voice_name]["ref_text"] = processed_text
            print(f"  - Voice '{voice_name}': Processed.")
        except Exception as e:
            print(f"Error processing reference for voice '{voice_name}': {e}")
            # Decide how to handle errors: skip voice, raise error?
            # For now, let's remove the problematic voice
            del all_voices[voice_name]
            print(f"    Skipping voice '{voice_name}'.")

    if "main" not in all_voices:
        raise ValueError("Main reference audio could not be processed.")

    # Inference Process
    generated_audio_segments = []
    final_sample_rate = None  # Will be set by infer_process

    # Regex for splitting text by voice tags like [voice_name]
    reg_split = r"(?=\[\w+\])"
    reg_extract = r"\[(\w+)\]"

    chunks = re.split(reg_split, gen_text)

    output_chunk_dir = None
    if save_chunk:
        output_chunk_dir = output_dir / f"{Path(output_file_name).stem}_chunks"
        output_chunk_dir.mkdir(parents=True, exist_ok=True)

    print("Starting inference...")
    for i, text_chunk in enumerate(chunks):
        if not text_chunk.strip():
            continue

        match = re.match(reg_extract, text_chunk)
        current_voice_name = "main"  # Default voice
        if match:
            extracted_voice = match.group(1)
            if extracted_voice in all_voices:
                current_voice_name = extracted_voice
            else:
                print(
                    f"Warning: Voice tag '[{extracted_voice}]' not found in provided voices. Using 'main'."
                )
            # Remove the tag from the text to be synthesized
            text_to_synthesize = re.sub(reg_extract, "", text_chunk).strip()
        else:
            text_to_synthesize = text_chunk.strip()
            # If no tag, assume it continues with the 'main' voice unless logic dictates otherwise

        if not text_to_synthesize:
            continue

        print(
            f"  - Synthesizing chunk {i+1} using voice '{current_voice_name}': '{text_to_synthesize[:50]}...'"
        )

        current_ref_audio = all_voices[current_voice_name]["ref_audio"]
        current_ref_text = all_voices[current_voice_name]["ref_text"]

        try:
            audio_segment, sr, _ = infer_process(
                current_ref_audio,
                current_ref_text,
                text_to_synthesize,
                ema_model,
                vocoder,
                mel_spec_type=vocoder_name,
                target_rms=target_rms,
                cross_fade_duration=cross_fade_duration,
                nfe_step=nfe_step,
                cfg_strength=cfg_strength,
                sway_sampling_coef=sway_sampling_coef,
                speed=speed,
                fix_duration=fix_duration,
                device=device,
            )
            generated_audio_segments.append(audio_segment)
            if final_sample_rate is None:
                final_sample_rate = sr

            if save_chunk and output_chunk_dir:
                chunk_filename = f"{i}_{text_to_synthesize[:30].replace(' ', '_')}.wav"
                chunk_path = output_chunk_dir / chunk_filename
                sf.write(str(chunk_path), audio_segment, sr)
                print(f"    Saved chunk: {chunk_path}")

        except Exception as e:
            print(f"Error during inference for chunk {i+1}: {e}")
            # Decide how to handle: skip chunk, stop entirely?
            print(f"    Skipping chunk: '{text_to_synthesize[:50]}...'")

    if not generated_audio_segments or final_sample_rate is None:
        print("No audio segments were generated.")
        return b"", final_sample_rate

    final_wave = np.concatenate(generated_audio_segments)
    if remove_silence:
        print(f"Removing silence (top_db={silence_top_db})...")
        try:
            trimmed_wave, _ = librosa.effects.trim(final_wave, top_db=silence_top_db)
            if len(trimmed_wave) < len(final_wave):
                final_wave = trimmed_wave
            else:
                print("No silence detected or removed.")
        except Exception as e:
            print(f"Error during silence removal: {e}")
    bytes_wav = io.BytesIO()
    try:
        sf.write(
            bytes_wav, final_wave, final_sample_rate, format="WAV", subtype="PCM_16"
        )
        wav_data = bytes_wav.getvalue()
        print("Encoding complete.")
        return wav_data, final_sample_rate
    except Exception as e:
        print(f"Error encoding audio to bytes: {e}")
        return b"", final_sample_rate
