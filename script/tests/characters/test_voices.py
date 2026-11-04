from tta_types.cast import NARRATOR_ID, Cast, CastMember
from tta_types.types import Voice
from tta_script.character.voices import choose_voice


def voice(name, age, gender):
    return Voice(name=name, age=age, gender=gender, audio_path="", audio_transcript="")


NARRATOR_VOICE = voice("narrator-voice", "middle-aged", "male")
YOUNG_MALE = voice("young-male", "young", "male")
YOUNG_FEMALE = voice("young-female", "young", "female")


def cast_with(*voice_names: str) -> Cast:
    members = [
        CastMember(id=NARRATOR_ID, names=["Narrator"], age="middle-aged", gender="male", voice="narrator-voice")
    ]
    members += [
        CastMember(id=f"c{i}", names=[f"c{i}"], age="young", gender="female", voice=v)
        for i, v in enumerate(voice_names, 1)
    ]
    return Cast(members=members)


def test_matching_unused_voice_is_chosen():
    voices = [NARRATOR_VOICE, YOUNG_MALE, YOUNG_FEMALE]

    assert choose_voice("young", "female", voices, cast_with()) == "young-female"


def test_no_matching_voice_falls_back_to_narrator():
    voices = [NARRATOR_VOICE, YOUNG_MALE]

    assert choose_voice("old", "female", voices, cast_with()) == "narrator-voice"


def test_voice_already_in_the_cast_is_not_reused():
    voices = [NARRATOR_VOICE, YOUNG_FEMALE]

    assert choose_voice("young", "female", voices, cast_with("young-female")) == "narrator-voice"


def test_without_a_narrator_the_first_voice_is_the_fallback():
    voices = [NARRATOR_VOICE, YOUNG_MALE]

    assert choose_voice("old", "female", voices, Cast()) == "narrator-voice"
