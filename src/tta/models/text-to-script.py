import re
import json

def convert_text_to_script_json():
    """
    Convert plain book text to a structured JSON-like format with speech items.
    Each item includes the text and the corresponding speaker (character or narrator).
    The speaker's name is inferred from the text.
    """
    # Prompt the user for book text input
    book_text = input("Please enter the book text: ")

    script = []
    current_speaker = "Narrator"
    
    # Matching dialogue in quores
    dialogue_pattern = re.compile(r'\"(.*?)\"')
    
    # This regular expression will help in detecting dialogue tags, such as 'said Bob', 'replied Mary'
    dialogue_tag_pattern = re.compile(r'(said|replied|asked)\s+([A-Z][a-z]+)')

    # Split text by sentence/paragraph, considering dialogues and non-dialogues
    parts = re.split(r'(\s*\".*?\"\s*)', book_text)

    for i, part in enumerate(parts):
        # Check if the part is dialogue or narration
        if dialogue_pattern.match(part.strip()):
            # This is a dialogue
            dialogue = part.strip().strip('"')
            # Look ahead to the next part for character name
            if i + 1 < len(parts):
                next_part = parts[i + 1]
                # Check if the next part contains a dialogue tag (e.g., "said Bob")
                match = dialogue_tag_pattern.search(next_part)
                if match:
                    current_speaker = match.group(2)  # Extract the character name (e.g., "Bob")
                else:
                    current_speaker = "Narrator"  # If no character is found, default to Narrator
            script.append({"text": dialogue, "speaker": current_speaker})
        else:
            # Non-dialogue part, so it's narration
            narration = part.strip()
            if narration:
                current_speaker = "Narrator"
                script.append({"text": narration, "speaker": current_speaker})

    return script

# Function call to process input and generate the script
script = convert_text_to_script_json()

# Output the script in JSON format for clarity
print(json.dumps(script, indent=2))
