from io import BytesIO

from tta_generator.character.extract import get_speaker_details
from tta_generator.dialogue.extract import get_dialogue_details
from tta_generator.voices import assign_voices
from tta_generator.character.types import SpeakerDetails
from tta_generator.voices import SpeakerVoice

from tta_speech.main import generate
from tta_types.types import Voice

from pydub import AudioSegment


def get_narration_from_text(
    text: str, voices: list[Voice], narrator_name: str
) -> bytes:
    speaker_voices = assign_voices(get_speaker_details(text), voices=voices)
    narrator_voice = SpeakerVoice(
        SpeakerDetails(frozenset({"Narrator"}), "middle-aged", "male"),
        next(voice for voice in voices if voice.name == narrator_name),
    )
    dialogue_details = get_dialogue_details(text, speaker_voices, narrator_voice)
    audio_segments = generate(
        dialogues=[(dialogue.text, dialogue.voice_id) for dialogue in dialogue_details],
        voices=voices,
    )
    return build_audio([audio_segments])


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
    import requests
    from pathlib import Path

    def get_text(filename: str) -> str:
        with open(
            f"{Path(__file__).parent}/../tests/text/{filename}", "r", encoding="utf-8"
        ) as f:
            return f.read()

    def get_voices_from_api() -> list[Voice]:
        response = requests.get("http://localhost:8000/voices")
        return [Voice(**voice) for voice in response.json()]

    voices: list[Voice] = get_voices_from_api()
    audio = get_narration_from_text(
        text=get_text("harrypotter-sample-tiny.txt"),
        voices=voices,
        narrator_name="Jim Dale",
    )
    with open("output.mp3", "wb") as f:
        f.write(audio)
