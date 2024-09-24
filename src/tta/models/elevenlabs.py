import os
from elevenlabs import ElevenLabs, VoiceSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the ElevenLabs client once
api_key = os.getenv('ELEVENLABS_API_KEY')
client = ElevenLabs(api_key=api_key)

def convert_text_to_speech_with_client(text: str, voice_id: str) -> bytes:
    """
    Converts text to speech using the ElevenLabs API and returns the audio as bytes.

    :param text: The text to convert to speech.
    :param voice_id: The voice ID to use for narration.
    :return: The bytes representation of the generated audio.
    """
    voice_settings = VoiceSettings(
        stability=0.5,
        similarity_boost=0.5
    )

    # Call the text-to-speech API and get the audio data
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        voice_settings=voice_settings,
        output_format="mp3_22050_32"  # Use a valid output format
    )

    # Collect the audio data from the generator
    audio_data = b''.join(audio_generator)

    return audio_data
