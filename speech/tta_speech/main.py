from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize

from fastapi import FastAPI

from tta_speech.infer import infer
from tta_speech.types import InferenceParams, VoiceName, Text, InputData

from tta_types.types import Voice


app = FastAPI()


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


def _prepare_input(
    dialogues: list[tuple[Text, VoiceName]],
    voices: list[Voice],
) -> InputData:
    def voice_to_dict(voice: Voice):
        return {
            "ref_audio": voice.audio_path,
            "ref_text": voice.audio_transcript,
        }

    def voices_from_names(voice_names: list[VoiceName]):
        return {
            voice.name: voice_to_dict(voice)
            for voice in voices
            if voice.name in voice_names
        }

    text = " ".join([f"[{voice_name}] {text}" for text, voice_name in dialogues])
    voices_dict = voices_from_names([voice_name for _, voice_name in dialogues])
    return InputData(text, voices_dict)


@app.post("/speech")
def generate(dialogues: list[tuple[Text, VoiceName]], voices: list[Voice]):
    text_input = _prepare_input(dialogues, voices)
    return infer(
        InferenceParams(
            gen_text=text_input.text,
            voices=text_input.voices,
            output_path="data/output.wav",
            vocab_file=f"{Path(__file__).parent}/vocab.txt",
            vocoder_name="vocos",
            vocoder_local_path=f"{Path(__file__).parent}/vocos",
            load_vocoder_from_local=True,
            remove_silence=True,
        )
    )
