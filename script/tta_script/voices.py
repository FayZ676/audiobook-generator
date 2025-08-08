from dataclasses import dataclass

from tta_types.types import Voice, Character


@dataclass(eq=True, frozen=True)
class Speaker:
    character: Character
    voice: Voice

    def first_alias(self) -> str:
        return self.character.first_alias()

    def to_dict(self) -> dict:
        return {
            "names": list(self.character.names),
            "age": self.character.age,
            "gender": self.character.gender,
            "voice_name": self.voice.name,
        }


def assign_voices(characters: set[Character], voices: list[Voice]) -> set[Speaker]:
    available_voices = voices
    voiced_characters = set()
    for character in characters:
        matching_voices = [
            voice
            for voice in available_voices
            if voice.age == character.age and voice.gender == character.gender
        ]

        if matching_voices:
            selected_voice = matching_voices[0]
            available_voices.remove(selected_voice)
            voiced_characters.add(Speaker(character=character, voice=selected_voice))
        else:
            raise ValueError(
                f"No available voices for {character.first_alias()} with age {character.age} and gender {character.gender}."
            )
    return voiced_characters
