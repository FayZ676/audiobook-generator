from dataclasses import dataclass

from tta_generator.character.types import SpeakerDetails

from tta_types.types import Voice


@dataclass(eq=True, frozen=True)
class SpeakerVoice:
    character: SpeakerDetails
    voice: Voice


def assign_voices(
    speakers: set[SpeakerDetails], voices: list[Voice]
) -> set[SpeakerVoice]:
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
            voiced_characters.add(SpeakerVoice(character=speaker, voice=selected_voice))
        else:
            raise ValueError(
                f"No available voices for {speaker.first_alias()} with age {speaker.age} and gender {speaker.gender}"
            )
    return voiced_characters
