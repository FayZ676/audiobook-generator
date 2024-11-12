from dataclasses import dataclass
from pydantic import BaseModel
from tta.models.text import generate_text_for_script
from tta.character import Character, CharacterVoiced, map_characters_to_voices
from tta.voices import VoiceCatalogue

@dataclass
class Speech:
    character: CharacterVoiced
    text: str

@dataclass
class Script:
    speeches: list[Speech]

class ResponseFormat(BaseModel):
    script: list[dict]  # A list of dicts, each containing a 'speaker' and 'text'

# Initialize VoiceCatalogue to retrieve voices
voice_catalogue = VoiceCatalogue()
all_voices = voice_catalogue.get_all_voices()

# Dynamic narrator voice selection based on preferred traits
def select_narrator_voice(voices):
    # Define preferred traits for a narrator voice
    preferred_traits = ["warm", "trustworthy", "expressive", "authoritative"]

    # Sort voices based on the priority of traits
    for trait in preferred_traits:
        for voice in voices:
            if trait in voice.traits.lower():
                return voice  # Return the first voice with a preferred trait

    # Fallback to any voice if none of the preferred traits are found
    return voices[0] if voices else None

# Select narrator voice dynamically
narrator_voice = select_narrator_voice(all_voices)
if narrator_voice:
    print(f"Selected Narrator Voice: ID: {narrator_voice.voice_id}, Name: {narrator_voice.name}, Traits: {narrator_voice.traits}")
else:
    raise RuntimeError("No voices available for narration.")

def convert_text_to_script(text: str, characters: list[CharacterVoiced]) -> Script | None:
    prompt = f"""
    <text>
    {text}
    </text>
    
    <characters>
    {", ".join([character.character.name for character in characters])}
    </characters>

    Convert the <text> into a verbatim script where every word is included. Assign all instances of speech to the appropriate character specified in <characters>. Assign all other instances of text to the Narrator.
    """

    try:
        result = generate_text_for_script(prompt)
        return parse_response(result, characters)
    except ValueError as e:
        print("Value error in generate_text or parse_response:", e)
    except TypeError as e:
        print("Type error in generate_text or parse_response:", e)

    return None

def parse_response(response: str, characters: list[CharacterVoiced]) -> Script | None:
    speeches = []
    narrator_character = CharacterVoiced(
        character=Character(name="Narrator", age="middle-aged", gender="neutral"),
        voice=narrator_voice
    )

    for line in response.splitlines():
        if not line.strip():
            continue
        parts = line.split(":", 1)
        if len(parts) != 2:
            print(f"Skipping line due to format issue: {line}")
            continue

        speaker_name, text = parts[0].strip(), parts[1].strip()
        character_voiced = next((cv for cv in characters if cv.character.name == speaker_name), None)

        if character_voiced:
            speeches.append(Speech(character=character_voiced, text=text))
        elif speaker_name.lower() == "narrator":
            speeches.append(Speech(character=narrator_character, text=text))
        else:
            print(f"Warning: Character '{speaker_name}' not found in provided character list.")

    return Script(speeches=speeches)

def main():
    # Sample text for testing with names of available voices
    text = """
    Aria walked carefully along the worn cobblestone path, her shoes clicking softly in the quiet evening air. "Roger, do you think we'll make it before sunset?" she asked, glancing up at the sky. The colors were changing rapidly, and the sun seemed to sink lower with each passing second.

    Roger, who was walking beside her, adjusted the basket hanging from his arm. "We should, if we keep moving," he said with a reassuring smile. His face was calm, though there was a faint crease in his brow that suggested he, too, was considering the time. The path ahead curved slightly, leading them into the woods, where the light from the setting sun would be harder to catch.

    Liam, a few paces behind, was running ahead, his laughter echoing through the trees. "I bet I can get there first!" he shouted, his voice full of excitement. His small feet pattered against the ground as he dashed forward. Aria watched him, her heart swelling with a mix of affection and concern.

    "Slow down, Liam!" Aria called out, but he was already too far ahead. He paused only when he reached the first big oak tree, panting and grinning. "I'm first!" he declared triumphantly.

    Roger caught up to Aria, shaking his head with a soft chuckle. "He never listens, does he?" he remarked, his tone warm but knowing. He looked at Aria, then back at Liam. "But that's what makes him so... Liam."

    Aria sighed, a fond smile playing at her lips. "I know. But I wish he'd slow down sometimes." She turned her gaze to the horizon, where the sun was nearly dipping below the treetops. "It’s so beautiful, though. Don’t you think?"

    Roger nodded, taking a deep breath of the cool evening air. "It is. We don’t see moments like this often enough. It’s easy to get caught up in everything else."

    Liam, who had been standing still for a moment, turned back and ran toward them. "You two are too slow!" he yelled, laughing as he approached. "Catch me if you can!"

    "He's got more energy than both of us combined," Aria muttered, though there was a playful edge to her voice. She began to run after him, her feet pounding against the path. Roger, still smiling, followed them both, his pace steady and measured.

    As they neared the edge of the woods, the colors in the sky shifted again, the first stars beginning to peek through the fading light. It was a perfect evening, one that none of them would forget. The laughter of the children echoed in the trees, while Roger’s soft chuckles and Aria’s gentle voice filled the air, all blending into the symphony of the night.
    """

    # Define sample characters based on available voices
    characters = [
        Character(name="Aria", age="middle-aged", gender="female"),
        Character(name="Roger", age="middle-aged", gender="male"),
        Character(name="Liam", age="young", gender="male")
    ]

    # Map characters to voices
    try:
        character_voiced_list = map_characters_to_voices(characters)
    except ValueError as e:
        print("Error mapping characters to voices:", e)
        return

    # Generate the script
    script = convert_text_to_script(text, character_voiced_list)

    # Check and print the result
    if script:
        print("Generated Script:")
        for speech in script.speeches:
            print(f"{speech.character.character.name} ({speech.character.voice.voice_id}): {speech.text}")
    else:
        print("Failed to generate script.")

# Run the main function if this file is executed
if __name__ == "__main__":
    main()
