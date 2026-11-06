from tta_script.cast import NARRATOR_ID, Age, Cast, Gender, Voice


def choose_voice(age: Age, gender: Gender, voices: list[Voice], cast: Cast) -> str:
    """The first unused voice matching age and gender, else the narrator's.

    A voice is used once any cast member has it, so every character keeps a
    distinct voice until matching voices run out."""
    used = {m.voice for m in cast.members}
    match = next(
        (v for v in voices if v.age == age and v.gender == gender and v.name not in used),
        None,
    )
    if match:
        return match.name
    narrator = cast.get(NARRATOR_ID)
    return narrator.voice if narrator else voices[0].name
