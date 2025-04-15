from pathlib import Path

from tta_tts.voices.labels import voices
from tta_tts.infer import infer


def generate(text: str, voice: str):
    voice_value = next((v for v in voices if v.name.lower() == voice.lower()), None)
    if not voice:
        raise ValueError(f"Voice '{voice}' not found.")
    audio = infer(
        ref_audio=voice_value.audio_path,  # type: ignore
        ref_text=voice_value.audio_transcript,  # type: ignore
        gen_text=text,
        output_path="data/output.wav",
        vocab_file=f"{Path(__file__).parent}/vocab.txt",
        device="mps",
    )
    return audio


# if __name__ == "__main__":
#     generate(
#         "Although this may sound like Faizi, this is in fact a computer generated voice made to sound like him. Don't freak out, I'll still make your story sound fantastic.",
#         "Faizi",
#     )
