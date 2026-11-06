from tta_script.cast import Age, Cast, Gender, Voice


def choose_voice(age: Age, gender: Gender, voices: list[Voice], cast: Cast) -> str | None:
    """The first voice matching age and gender that no cast member has yet,
    or None once those run out.

    Every character keeps a distinct voice. None is left for a person to fill
    rather than reusing a voice, which would make two characters sound alike."""
    used = {m.voice for m in cast.members}
    return next(
        (v.name for v in voices if v.age == age and v.gender == gender and v.name not in used),
        None,
    )
