import logging

from tta_types.cast import NARRATOR_ID, Cast, CastMember
from tta_types.types import Voice
from tta_script.models.text import generate_text
from tta_script.utils.text import get_chunks
from tta_script.character.prompts import cast_update
from tta_script.character.types import CastUpdate
from tta_script.character.voices import choose_voice


logger = logging.getLogger(__name__)

# Keeps each request under 100K tokens, where Claude Haiku 5.5's price rises.
CHUNK_WORDS = 60_000


def update_cast(text: str, cast: Cast, voices: list[Voice]) -> Cast:
    """Return a copy of cast that includes everyone who speaks in text.

    New characters get the next id and a voice; known characters gain any new
    names the text uses for them. The first chapter also adds the narrator,
    who reads in the first voice."""
    if not voices:
        raise ValueError("No voices available")
    cast = cast.model_copy(deep=True)
    if cast.get(NARRATOR_ID) is None:
        cast.members.append(
            CastMember(
                id=NARRATOR_ID,
                names=["Narrator"],
                age="middle-aged",
                gender="male",
                voice=voices[0].name,
            )
        )

    for chunk in get_chunks(text, CHUNK_WORDS):
        prompt = cast_update.substitute(text=chunk, known_characters=_render_known(cast))
        update = CastUpdate.model_validate_json(generate_text("", prompt, CastUpdate))
        _apply(update, cast, voices)
    return cast


def _render_known(cast: Cast) -> str:
    lines = [f"- {m.id}: {', '.join(m.names)}" for m in cast.members if m.id != NARRATOR_ID]
    return "\n".join(lines) or "(none)"


def _apply(update: CastUpdate, cast: Cast, voices: list[Voice]) -> None:
    for known in update.known:
        member = cast.get(known.id)
        if member is None or member.id == NARRATOR_ID:
            logger.warning("Model referred to unknown character id %r; ignoring", known.id)
            continue
        _add_names(member, known.new_names)

    for new in update.new:
        names = _clean(new.names)
        if not names or "Narrator" in names:
            continue
        # Safety net: a "new" character whose name exactly matches exactly one
        # known character is almost certainly that character.
        matches = [m for m in cast.members if m.id != NARRATOR_ID and _shares_name(m, names)]
        if len(matches) == 1:
            logger.info("Merging new %r into known %s", names, matches[0].id)
            _add_names(matches[0], names)
            continue
        cast.members.append(
            CastMember(
                id=cast.next_id(),
                names=names,
                age=new.age,
                gender=new.gender,
                voice=choose_voice(new.age, new.gender, voices, cast),
            )
        )


def _clean(names: list[str]) -> list[str]:
    return list(dict.fromkeys(n.strip() for n in names if n.strip()))


def _add_names(member: CastMember, names: list[str]) -> None:
    for name in _clean(names):
        if name.lower() not in {n.lower() for n in member.names}:
            member.names.append(name)


def _shares_name(member: CastMember, names: list[str]) -> bool:
    return bool({n.lower() for n in member.names} & {n.lower() for n in names})
