from io import BytesIO

from tta.character.extract import get_speaker_details
from tta.dialogue import get_dialogue
from tta.models.speech import get_speech
from tta.voices import get_voices

from pydub import AudioSegment


def get_narration_from_text(text: str) -> bytes:
    names = get_speaker_details(text)
    script = get_dialogue(text, {name.first_alias() for name in names})
    voices = get_voices(names)
    # TODO: Implement voice selection logic
    audio_segments = [
        get_speech(text=item.text, voice_id=item.voice_id) for item in script
    ]
    return build_audio(audio_segments)


def build_audio(audio_segments: list) -> bytes:
    combined = AudioSegment.empty()
    for audio_bytes in audio_segments:
        segment = AudioSegment.from_file(BytesIO(audio_bytes))
        combined += segment

    output = BytesIO()
    combined.export(output, format="mp3")
    return output.getvalue()
