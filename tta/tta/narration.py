from io import BytesIO

from tta.character import identify_characters
from tta.script import convert_text_to_script
from tta.models.speech import generate_speech

from pydub import AudioSegment


def get_narration_from_text(text: str) -> bytes:
    characters = identify_characters(text)
    script = convert_text_to_script(text, characters)
    narration_audio = [generate_speech(item.text, item.voice_id) for item in script]

    # Combine audio segments
    combined = AudioSegment.empty()
    for audio_bytes in narration_audio:
        segment = AudioSegment.from_file(BytesIO(audio_bytes))
        combined += segment

    # Export to bytes
    output = BytesIO()
    combined.export(output, format="mp3")
    return output.getvalue()
