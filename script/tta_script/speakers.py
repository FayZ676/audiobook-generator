from tta_types.types import Voice, Character, Speaker


def get_speakers(
    characters: set[Character],
    voices: list[Voice],
    narrator_voice: Voice,
    previous_speakers: set[Speaker],
) -> set[Speaker]:

    speakers: set[Speaker] = set()
    available_voices = voices.copy()

    for character in characters:
        speaker = _get_speaker_for_character(character, previous_speakers)
        if speaker:
            speakers.add(speaker)
            if speaker.voice in available_voices:
                available_voices.remove(speaker.voice)
            continue

        voice = _assign_voice_to_character(character, available_voices, narrator_voice)
        speakers.add(Speaker(character=character, voice=voice))

    return speakers


def _get_character_voice(
    character: Character, available_voices: list[Voice]
) -> Voice | None:
    return next(
        (
            voice
            for voice in available_voices
            if voice.age == character.age and voice.gender == character.gender
        ),
        None,
    )


def _get_speaker_for_character(character: Character, speakers: set[Speaker]):
    return next(
        (
            speaker
            for speaker in speakers
            if any(name in speaker.character.names for name in character.names)
        ),
        None,
    )


def _assign_voice_to_character(
    character: Character, available_voices: list[Voice], narrator_voice: Voice
) -> Voice:
    voice = _get_character_voice(character, available_voices)
    if voice:
        available_voices.remove(voice)
        return voice
    return narrator_voice
