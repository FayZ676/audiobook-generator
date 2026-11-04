from tta_script.models.text import generate_text
from tta_script.utils.text import get_chunks
from tta_script.character.prompts import characters as characters_prompt
from tta_script.character.types import CharactersResponse
from tta_types.types import Character


NARRATOR = Character(names=["Narrator"], age="middle-aged", gender="male")

# Keeps each request under 100K tokens, where Claude Haiku 5.5's price rises.
CHUNK_WORDS = 60_000


def get_characters(text: str, existing_characters: set[Character]) -> set[Character]:
    """Find the speaking characters in text that aren't already known.

    The narrator is added on the first chapter, when nothing is known yet."""
    new_characters: set[Character] = set()
    for chunk in get_chunks(text, CHUNK_WORDS):
        known = existing_characters | new_characters
        new_characters.update(
            c for c in _find_characters(chunk, known) if not _overlaps(c, known)
        )

    if not existing_characters:
        new_characters.add(NARRATOR)
    return new_characters


def _find_characters(text: str, known: set[Character]) -> list[Character]:
    prompt = characters_prompt.substitute(
        text=text,
        known_characters="\n".join(f"- {', '.join(c.names)}" for c in known) or "(none)",
    )
    response = CharactersResponse.model_validate_json(
        generate_text("", prompt, CharactersResponse)
    )
    found = []
    for c in response.characters:
        names = list(dict.fromkeys(n.strip() for n in c.names if n.strip()))
        if names and "Narrator" not in names:
            found.append(Character(names=names, age=c.age, gender=c.gender))
    return found


def _overlaps(character: Character, known: set[Character]) -> bool:
    """Whether character shares a name with someone already known."""
    names = set(character.names)
    return any(names & set(k.names) for k in known)
