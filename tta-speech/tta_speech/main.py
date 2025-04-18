from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize

from tta_speech.voices.labels import voices as Voices
from tta_speech.infer import infer
from tta_speech.types import InferenceParams, VoiceName, Text, InputData


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


def prepare_input(dialogues: list[tuple[Text, VoiceName]]) -> InputData:
    def voices_from_names(voice_names: list[VoiceName]):
        return {
            voice.name: voice.audio_to_dict()
            for voice in Voices
            if voice.name in voice_names
        }

    text = " ".join([f"[{voice_name}] {text}" for text, voice_name in dialogues])
    voices = voices_from_names([voice_name for _, voice_name in dialogues])
    return InputData(text, voices)


def generate(dialogues: list[tuple[Text, VoiceName]]):
    input = prepare_input(dialogues)
    return infer(
        InferenceParams(
            gen_text=input.text,
            voices=input.voices,
            output_path="data/output.wav",
            vocab_file=f"{Path(__file__).parent}/vocab.txt",
            vocoder_name="vocos",
            vocoder_local_path=f"{Path(__file__).parent}/vocos",
            load_vocoder_from_local=True,
            device="mps",
            remove_silence=True,
        )
    )


if __name__ == "__main__":
    normalize_audio_volume(
        f"{Path(__file__).parent}/voices/audios/stephen_fry.mp3", headroom=0.1
    )
