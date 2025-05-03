from io import BytesIO
from pathlib import Path
from pydub import AudioSegment
from pydub.effects import normalize

from fastapi import FastAPI

from tta_speech.infer import infer
from tta_speech.types import InferenceParams, InputData, SpeechRequest, TextSegment

from tta_types.types import Voice
from tta_aws.s3 import S3Client


app = FastAPI()


s3 = S3Client()
SPEECH_BUCKET = "tta-speech-results"
VOICES_AUDIOS_BUCKET = "tta-voices-audios"


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


# NOTE: I hate that we need to download the audio.
def _prepare_input(
    request: list[TextSegment], voices: list[Voice], voice_save_path: str
) -> InputData:
    def download_audio(audio_name: str):
        print(f"Downloading audio {audio_name}")
        audio = s3.get_file(VOICES_AUDIOS_BUCKET, f"{audio_name}.mp3")
        audio_file = BytesIO(audio)
        temp_audio_path = f"{voice_save_path}/{audio_name}"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_file.read())
        return temp_audio_path

    def voice_to_dict(path, transcript):
        return {
            "ref_audio": path,
            "ref_text": transcript,
        }

    def voices_from_names(voice_names: list[str]):
        return {
            voice.name: voice_to_dict(
                path=download_audio(voice.name.lower().replace(" ", "_")),
                transcript=voice.audio_transcript,
            )
            for voice in voices
            if voice.name in voice_names
        }

    text = " ".join([f"[{r.voice_name}] {r.text}" for r in request])
    voices_dict = voices_from_names([r.voice_name for r in request])
    return InputData(text, voices_dict)


def _build_audio(audio_segments: list[tuple[bytes, int | None]]) -> bytes:
    combined = AudioSegment.empty()
    for audio_bytes, sample_rate in audio_segments:
        segment = AudioSegment.from_file(
            BytesIO(audio_bytes), format="wav", frame_rate=sample_rate
        )
        combined += segment

    output = BytesIO()
    combined.export(output, format="mp3")
    return output.getvalue()


@app.post("/speech")
def generate(request: SpeechRequest, voices: list[Voice]):
    voice_save_path = "/tmp"
    text_input = _prepare_input(request.text, voices, voice_save_path)
    result = infer(
        InferenceParams(
            gen_text=text_input.text,
            voices=text_input.voices,
            vocab_file=f"{Path(__file__).parent}/vocab.txt",
            vocoder_name="vocos",
            vocoder_local_path=f"{Path(__file__).parent}/vocos",
            load_vocoder_from_local=True,
            remove_silence=True,
        )
    )
    audio = _build_audio([result])
    s3.upload_fileobj(SPEECH_BUCKET, f"{request.title}.mp3", BytesIO(audio))
    # TODO: Send notification to webhook.
