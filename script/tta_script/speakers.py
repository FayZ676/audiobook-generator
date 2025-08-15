from tta_types.types import Voice, Character, Speaker


def get_speakers(
    characters: set[Character],
    voices: list[Voice],
    previous_speakers: set[Speaker],
) -> set[Speaker]:

    available_voices = voices.copy()
    speakers: set[Speaker] = set()
    
    # Find the Narrator voice for fallback
    narrator_voice = next(
        (voice for voice in voices if voice.name == "Narrator"),
        None
    )

    for character in characters:
        existing_speaker = next(
            (
                speaker
                for speaker in previous_speakers
                if any(name in speaker.character.names for name in character.names)
            ),
            None,
        )

        if existing_speaker:
            speakers.add(existing_speaker)
            if existing_speaker.voice in available_voices:
                available_voices.remove(existing_speaker.voice)
        else:
            matching_voices = [
                voice
                for voice in available_voices
                if voice.age == character.age and voice.gender == character.gender
            ]

            if matching_voices:
                selected_voice = matching_voices[0]
                available_voices.remove(selected_voice)
                speakers.add(Speaker(character=character, voice=selected_voice))
            else:
                # Fallback to Narrator voice if available
                if narrator_voice:
                    speakers.add(Speaker(character=character, voice=narrator_voice))
                else:
                    raise ValueError(
                        f"No available voices for {character.first_alias()} with age {character.age} and gender {character.gender}, and no Narrator voice found."
                    )

    return speakers
