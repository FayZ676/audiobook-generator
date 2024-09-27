import os
from elevenlabs.client import VoiceSettings, ElevenLabs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the ElevenLabs client once
api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)


def generate_speech(text: str, voice_id: str) -> bytes:
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.5),
        output_format="mp3_22050_32",  #
    )
    return b"".join(audio_generator)
