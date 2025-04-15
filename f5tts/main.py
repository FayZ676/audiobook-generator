from voices.labels import voices
from infer import infer


def generate(text: str, voice: str):
    voice_value = next((v for v in voices if v.name.lower() == voice.lower()), None)
    if not voice:
        raise ValueError(f"Voice '{voice}' not found.")
    audio = infer(
        ref_audio=voice_value.audio_path,  # type: ignore
        ref_text=voice_value.audio_transcript,  # type: ignore
        gen_text=text,
        output_path="output.wav",
        vocab_file="F5-TTS/src/f5_tts/infer/examples/vocab.txt",
        device="mps",
    )

    with open("output.wav", "wb") as f:
        f.write(audio)


if __name__ == "__main__":
    generate(
        "Although this may sound like Faizi, this is in fact a computer generated voice made to sound like him. Don't freak out, I'll still make your story sound fantastic.",
        "Faizi",
    )
