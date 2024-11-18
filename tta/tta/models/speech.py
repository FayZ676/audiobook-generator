import os
from elevenlabs.client import ElevenLabs, VoiceId
from dotenv import load_dotenv


load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))


def generate_speech(text: str, voice_id: str) -> bytes:
    audio_generator = client.generate(
        voice=VoiceId(voice_id), text=text, model="eleven_turbo_v2_5"
    )
    audio_chunks = list(audio_generator)
    return b"".join(audio_chunks)
