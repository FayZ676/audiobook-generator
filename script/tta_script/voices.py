from dataclasses import dataclass

from tta_script.character.types import SpeakerDetails

from tta_types.types import Voice, CharacterVoiceMappings


@dataclass(eq=True, frozen=True)
class Speaker:
    character: SpeakerDetails
    voice: Voice

    def first_alias(self) -> str:
        return self.character.first_alias()

    def to_dict(self) -> dict:
        return {
            "names": list(self.character.names),
            "age": self.voice.age,
            "gender": self.voice.gender,
            "voice_name": self.voice.name,
        }


def assign_voices(
    speakers: set[SpeakerDetails], 
    voices: list[Voice], 
    character_voice_mappings: CharacterVoiceMappings | None = None
) -> set[Speaker]:
    character_voice_mappings = character_voice_mappings or {}
    available_voices = voices.copy()
    voiced_characters = set()
    assigned_speaker_names = set()
    
    # First pass: assign voices based on existing mappings
    for speaker in speakers:
        speaker_name = speaker.first_alias()
        if speaker_name in character_voice_mappings:
            mapped_voice_name = character_voice_mappings[speaker_name]
            # Find the voice by name
            mapped_voice = next(
                (voice for voice in available_voices if voice.name == mapped_voice_name), 
                None
            )
            if mapped_voice:
                available_voices.remove(mapped_voice)
                voiced_characters.add(Speaker(character=speaker, voice=mapped_voice))
                assigned_speaker_names.add(speaker_name)
    
    # Second pass: assign remaining speakers to available voices
    for speaker in speakers:
        speaker_name = speaker.first_alias()
        if speaker_name not in assigned_speaker_names:
            matching_voices = [
                voice
                for voice in available_voices
                if voice.age == speaker.age and voice.gender == speaker.gender
            ]

            if matching_voices:
                selected_voice = matching_voices[0]
                available_voices.remove(selected_voice)
                voiced_characters.add(Speaker(character=speaker, voice=selected_voice))
            else:
                raise ValueError(
                    f"No available voices for {speaker.first_alias()} with age {speaker.age} and gender {speaker.gender}."
                )
    
    return voiced_characters
