from io import BytesIO

from tta.character.extract import get_speaker_details
from tta.dialogue.extract import get_dialogue_details
from tta.voices import get_voices

from tta_speech.main import generate

from pydub import AudioSegment


def preprocess_text(text: str) -> str:
    text = text.strip()
    if text.endswith(","):
        text = text[:-1] + "."
    return text[0].upper() + text[1:] + " "


def get_narration_from_text(text: str) -> bytes:
    speaker_voices = get_voices(get_speaker_details(text))
    dialogue_details = get_dialogue_details(text, speaker_voices)
    audio_segments = [
        generate(preprocess_text(dialogue.text), dialogue.voice_id)
        for dialogue in dialogue_details
    ]
    return build_audio(audio_segments)


def build_audio(audio_segments: list[tuple[bytes, int | None]]) -> bytes:
    combined = AudioSegment.empty()
    for audio_bytes, sample_rate in audio_segments:
        segment = AudioSegment.from_file(
            BytesIO(audio_bytes), format="wav", frame_rate=sample_rate
        )
        combined += segment

    output = BytesIO()
    combined.export(output, format="mp3")
    return output.getvalue()


if __name__ == "__main__":
    from pathlib import Path

    def get_text(filename: str) -> str:
        with open(
            f"{Path(__file__).parent}/../tests/text/{filename}", "r", encoding="utf-8"
        ) as f:
            return f.read()

    audio = get_narration_from_text(get_text("harrypotter-sample-tiny.txt"))
    with open("output.mp3", "wb") as f:
        f.write(audio)
