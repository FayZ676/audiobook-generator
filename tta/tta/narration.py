from io import BytesIO

from tta.character import identify_characters, Character
from tta.script import convert_text_to_script
from tta.models.speech import generate_speech
from tta.text_handler import get_chunks
from tta.voices import map_characters_to_voices

from pydub import AudioSegment


def get_narration_from_text(text: str) -> bytes:
    characters = identify_characters(text, set())
    characters_voiced = map_characters_to_voices(characters)
    script = convert_text_to_script(text, characters_voiced)
    for item in script:
        print(item)
    narration_audio = [
        generate_speech(text=item.text, voice_id=item.voice_id) for item in script
    ]

    # Combine audio segments
    combined = AudioSegment.empty()
    for audio_bytes in narration_audio:
        segment = AudioSegment.from_file(BytesIO(audio_bytes))
        combined += segment

    # Export to bytes
    output = BytesIO()
    combined.export(output, format="mp3")
    return output.getvalue()


def get_narration(texts: list[str]):
    known_characters: set[Character] = set()
    for text in texts:
        characters = identify_characters(text, {char.name for char in known_characters})
        known_characters.update(characters)
    return known_characters


if __name__ == "__main__":
    with open("../tests/text/harrypotter-1-3.txt") as file:
        content = file.read()
    chunks = get_chunks(content, 500)
    result = get_narration(chunks)
    for r in result:
        print(r.name)
