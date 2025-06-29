from dataclasses import dataclass

from tta_script.character.types import SpeakerDetails

from tta_types.types import Voice


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
            "audio_path": self.voice.audio_path,
            "audio_transcript": self.voice.audio_transcript,
        }


def assign_voices(
    speakers: set[SpeakerDetails], voices: list[Voice]
) -> set[Speaker]:
    available_voices = voices
    voiced_characters = set()
    for speaker in speakers:
        matching_voices = [
            voice
            for voice in available_voices
            if voice.age == speaker.age and voice.gender == speaker.gender
        ]

        if matching_voices:
            selected_voice = matching_voices[0]
            available_voices.remove(selected_voice)
            # Create Speaker directly without conversion
            voiced_characters.add(Speaker(character=speaker, voice=selected_voice))
        else:
            raise ValueError(
                f"No available voices for {speaker.first_alias()} with age {speaker.age} and gender {speaker.gender}."
            )
    return voiced_characters
