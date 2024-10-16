from typing import List
from dataclasses import dataclass
from tta.character import Character 
from tta.voices import Voice, voices_catalogue 

@dataclass
class CharacterVoiced:
    character: Character
    voice: Voice

def map_characters_to_voices(characters: List[Character]) -> List[CharacterVoiced]:
    available_voices = voices_catalogue[:]  # Copy of available voices
    voiced_characters = []  # To store final mapped voices

    # Loop over characters
    for character in characters:
        matching_voices = [
            voice for voice in available_voices
            if voice.age_group == character.age and voice.gender == character.gender
        ]

        if matching_voices:
            selected_voice = matching_voices[0]
            available_voices.remove(selected_voice)
            voiced_characters.append(CharacterVoiced(character=character, voice=selected_voice))
        else:
            raise ValueError(f"No available voices for {character.name} with age {character.age} and gender {character.gender}")

    return voiced_characters
