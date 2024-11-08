from dataclasses import dataclass
from pydantic import BaseModel
from tta.models.text import generate_text_for_script
from tta.character import Character, CharacterVoiced, map_characters_to_voices
from tta.voices import voices_catalogue

@dataclass
class Speech:
    character: CharacterVoiced  # Use CharacterVoiced to include character and voice data
    text: str

@dataclass
class Script:
    speeches: list[Speech]  # List of Speech objects as before

class ResponseFormat(BaseModel):
    script: list[dict]  # Expect a list of dicts where each dict contains a 'speaker' and 'text'

narrator_voice = next((voice for voice in voices_catalogue if voice.id == "narrator"), None)

if narrator_voice is None:
    raise RuntimeError("Narrator voice not found in voices_catalogue")

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
    except Exception as e:
        print("Unexpected error in generate_text or parse_response:", e)

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
