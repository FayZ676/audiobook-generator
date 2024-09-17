from gtts import gTTS
import tempfile
import os

# Function to generate text-to-speech and save as MP3
def text_to_speech(text):
    if text is None:
        return None

    try:
        # Initialize gTTS and convert text to speech
        tts = gTTS(text, lang='en')
        
        # Use a temporary file for the MP3 output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
            mp3_path = temp_mp3.name
            tts.save(mp3_path)
            print(f"MP3 file saved at: {mp3_path}")
            return mp3_path
    except Exception as e:
        print(f"Error generating or saving MP3: {e}")
        return None

# Function to generate text using OpenAI's chat model
def generate_text_from_prompt(prompt):
    import openai

    # Replace with your OpenAI API key
    openai.api_key = 'xxx'

    try:
        # Call the OpenAI API to get the generated text
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a narrator for an audiobook."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        generated_text = response.choices[0].message['content']
        return generated_text
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

# Main function to handle the process
def main(prompt):
    generated_text = generate_text_from_prompt(prompt)
    if generated_text:
        mp3_file_path = text_to_speech(generated_text)
        if mp3_file_path:
            print(f"MP3 generated at: {mp3_file_path}")
        else:
            print("Failed to convert text to speech.")
    else:
        print("Failed to generate text.")

if __name__ == "__main__":
    prompt = input("Enter the prompt: ")
    main(prompt)
