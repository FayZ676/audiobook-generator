from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize

from tta_tts.voices.labels import voices
from tta_tts.infer import infer


def normalize_audio_volume(audio_path: str, headroom: float = 0.1) -> str:
    try:
        audio = AudioSegment.from_file(audio_path)
        normalized_audio = normalize(audio, headroom=headroom)
        file_format = Path(audio_path).suffix.lstrip(".")
        normalized_audio.export(audio_path, format=file_format)
        return audio_path
    except Exception as e:
        print(f"Error normalizing audio file {audio_path}: {e}")
        return audio_path


def generate(text: str, voice: str):
    voice_value = next((v for v in voices if v.name.lower() == voice.lower()), None)
    if not voice:
        raise ValueError(f"Voice '{voice}' not found.")
    return infer(
        ref_audio=voice_value.audio_path,  # type: ignore
        ref_text=voice_value.audio_transcript,  # type: ignore
        gen_text=text,
        output_path="data/output.wav",
        vocab_file=f"{Path(__file__).parent}/vocab.txt",
        device="mps",
    )


if __name__ == "__main__":
    normalize_audio_volume(
        f"{Path(__file__).parent}/voices/audios/elizabeth_gaskell.mp3", headroom=0.1
    )
