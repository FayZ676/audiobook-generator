import requests

class ElevenLabsAPI:
    def __init__(self):
        # Set the API key and the base URL
        self.api_key = "sk_9fd4a07f29c92669de3b77ece2efeb060f2f7b92f9e052f5" # Your ElevenLabs API Key
        self.base_url = "https://api.elevenlabs.io/v1/text-to-speech/"
    
    def convert_text_to_speech(self, text, voice_id, output_format="audio/mpeg", stability=0.5, similarity_boost=0.5):
        """
        Converts the provided text to speech using the ElevenLabs API.

        :param text: The text to convert to speech.
        :param voice_id: The voice ID to use for narration.
        :param output_format: The desired output format.
        :param stability: Voice stability.
        :param similarity_boost: Similarity boost for the voice.
        :return: The path to the saved audio file if successful.
        """
        # Set the request URL
        url = self.base_url + voice_id

        # Set up the headers for the request
        headers = {
            "Accept": output_format,
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        # Prepare the data payload for the API request
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",  # Use default model or specify another one
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
            }
        }

        # Make the POST request to ElevenLabs API
        response = requests.post(url, json=data, headers=headers)

        # Process response
        if response.status_code == 200:
            # Save the audio to a file
            output_file_path = "output.mp3"
            with open(output_file_path, 'wb') as audio_file:
                audio_file.write(response.content)  # Write received audio file
            return output_file_path
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

# Example usage
if __name__ == "__main__":
    eleven_labs_api = ElevenLabsAPI()
    
    try:
        # Sample text and voice ID
        sample_text = "It sure does, Jackie… My mama always said: “In Carolina, the air's so thick you can wear it!”"
        voice_id = "pMsXgVXv3BLzUgSXRplE"  # Replace with your desired voice ID

        # Call the function to convert text to speech
        audio_output_path = eleven_labs_api.convert_text_to_speech(sample_text, voice_id)
        print(f"Audio successfully saved to: {audio_output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
