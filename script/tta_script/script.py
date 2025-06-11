from tta_script.character.extract import get_speaker_details
from tta_script.dialogue.extract import get_dialogue_details
from tta_script.voices import assign_voices
from tta_script.character.types import SpeakerDetails
from tta_script.voices import SpeakerVoice

from tta_types.types import Voice


def generate_script(text: str, voices: list[Voice], narrator_name: str):
    speaker_voices = assign_voices(get_speaker_details(text), voices=voices)
    narrator_voice = next(voice for voice in voices if voice.name == narrator_name)
    narrator_speaker = SpeakerVoice(
        SpeakerDetails(
            frozenset({"Narrator"}), narrator_voice.age, narrator_voice.gender  # type: ignore
        ),
        narrator_voice,
    )
    return get_dialogue_details(text, speaker_voices, narrator_speaker)
