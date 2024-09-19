import os
from elevenlabs import ElevenLabs, VoiceSettings

from dotenv import load_dotenv

load_dotenv()

def convert_text_to_speech_with_client(text, voice_id, api_key):
    client = ElevenLabs(api_key=api_key)

    voice_settings = VoiceSettings(
        stability=0.5,
        similarity_boost=0.5
    )

    # Correct your output format
    audio_generator = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        voice_settings=voice_settings,
        output_format="mp3_22050_32"  # Change to a valid format
    )

    output_file_path = "output.mp3"
    with open(output_file_path, 'wb') as audio_file:
        if hasattr(audio_generator, '__iter__'):
            for audio_chunk in audio_generator:
                audio_file.write(audio_chunk)
        else:
            audio_file.write(audio_generator)

    return output_file_path

# Usage
if __name__ == "__main__":
    api_key = os.getenv('ELEVENLABS_API_KEY')
    sample_text = "It sure does, Jackie… My mama always said: “In Carolina, the air's so thick you can wear it!”"
    voice_id = "pMsXgVXv3BLzUgSXRplE"

    try:
        audio_output_path = convert_text_to_speech_with_client(sample_text, voice_id, api_key)
        print(f"Audio successfully saved to: {audio_output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
