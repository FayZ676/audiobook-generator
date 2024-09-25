from openai import OpenAI

client = OpenAI(api_key='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')
import json

# Set your OpenAI API key

def identify_characters(paragraph):
    # Define the prompt to send to the API
    prompt = f"Analyze the following paragraph and identify the speaking characters, their age (categorized as young, middle-aged, or old), and gender:\n\n{paragraph}\n\nProvide the information in the format: Character: [Name], Age: [young/middle-aged/old], Gender: [Gender]."

    # Make the API call
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Use 'gpt-3.5-turbo' or 'gpt-4'
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=150,
    temperature=0.5)

    # Extract the response text
    result = response.choices[0].message.content.strip()
    return result

# Example paragraph
paragraph = """
Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview. Our clients were punctual to their appointment, for the clock had just struck ten when Dr. Mortimer was shown up, followed by the young baronet. The latter was a small, alert, dark-eyed man about thirty years of age, very sturdily built, with thick black eyebrows and a strong, pugnacious face. He wore a ruddy-tinted tweed suit and had the weather-beaten appearance of one who has spent most of his time in the open air, and yet there was something in his steady eye and the quiet assurance of his bearing which indicated the gentleman.

“This is Sir Henry Baskerville,” said Dr. Mortimer.

“Why, yes,” said he, “and the strange thing is, Mr. Sherlock Holmes, that if my friend here had not proposed coming round to you this morning I should have come on my own account. I understand that you think out little puzzles, and I’ve had one this morning which wants more thinking out than I am able to give it.”

“Pray take a seat, Sir Henry. Do I understand you to say that you have yourself had some remarkable experience since you arrived in London?”

“Nothing of much importance, Mr. Holmes. Only a joke, as like as not. It was this letter, if you can call it a letter, which reached me this morning.”
"""

# Identify characters
characters_info = identify_characters(paragraph)

# Save the output to a JSON file
output_file = 'characters_info.json'
with open(output_file, 'w') as f:
    json.dump(characters_info, f)

print(f"Character information saved to {output_file}")
