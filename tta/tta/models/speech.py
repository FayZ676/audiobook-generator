import os
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv


load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


def generate_speech(text: str, voice_id: str) -> bytes:
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        output_format="mp3_22050_32",  #
    )
    return b"".join(audio_generator)
