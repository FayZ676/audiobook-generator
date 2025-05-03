from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize

from fastapi import FastAPI

from tta_speech.infer import infer
from tta_speech.types import InferenceParams, InputData, SpeechRequest

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
    request: list[SpeechRequest],
    voices: list[Voice],
) -> InputData:
    def voice_to_dict(voice: Voice):
        return {
            "ref_audio": voice.audio_path,
            "ref_text": voice.audio_transcript,
        }

    def voices_from_names(voice_names: list[str]):
        return {
            voice.name: voice_to_dict(voice)
            for voice in voices
            if voice.name in voice_names
        }

    text = " ".join([f"[{r.voice_name}] {r.text}" for r in request])
    voices_dict = voices_from_names([r.voice_name for r in request])
    return InputData(text, voices_dict)


@app.post("/speech")
def generate(request: list[SpeechRequest], voices: list[Voice]):
    text_input = _prepare_input(request, voices)
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
