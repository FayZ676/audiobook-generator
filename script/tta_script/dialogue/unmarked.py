"""Find speech in a chapter that doesn't mark it with quotes or dashes, as
Cormac McCarthy and Sally Rooney write, perhaps apart from a few quoted
lines. The model points at the words spoken aloud; those not already in
quotes are put in them, so the usual splitter can split the chapter."""

import logging
from string import Template

from pydantic import BaseModel

from tta_script.dialogue.extract import CLOSE, OPEN, marks_its_speech
from tta_script.models.text import generate_text


logger = logging.getLogger(__name__)


class SpokenParagraph(BaseModel):
    paragraph: int
    spoken: list[str]


class SpokenLines(BaseModel):
    paragraphs: list[SpokenParagraph]


PROMPT = Template(
    """
## Text
Numbered paragraphs. The text mostly doesn't mark speech with quotation marks or dashes.
$text

## Instructions
For each paragraph containing words a character speaks or sings aloud, list those words, copied exactly as they appear, as separate strings in the order they appear. Include speech whether or not it is in quotation marks, but leave the quotation marks out of the strings. Split a paragraph's speech wherever narration interrupts it.

## Rules
- Leave out narration, including attributions such as "he said" or "she asked".
- Leave out thoughts and words that aren't said aloud.
- Leave out paragraphs with no speech.
"""
)


def mark_spoken_lines(text: str) -> str:
    """Return text with its speech in quotes. Text that already marks its
    speech is returned unchanged, without calling the model."""
    if marks_its_speech(text):
        return text
    paragraphs = [" ".join(p.split()) for p in text.split("\n\n") if p.strip()]
    numbered = "\n\n".join(f"{i}. {p}" for i, p in enumerate(paragraphs))
    reply = SpokenLines.model_validate_json(
        generate_text("", PROMPT.substitute(text=numbered), SpokenLines)
    )
    for found in reply.paragraphs:
        if 0 <= found.paragraph < len(paragraphs):
            paragraphs[found.paragraph] = _quote(paragraphs[found.paragraph], found.spoken)
    return "\n\n".join(paragraphs)


def _quote(paragraph: str, spoken: list[str]) -> str:
    """Put each spoken passage in quotes, searching on from the last one.
    A passage the paragraph doesn't contain, word for word, is skipped, and
    so is one already in quotes."""
    start = 0
    for words in (" ".join(w.split()) for w in spoken):
        at = paragraph.find(words, start) if words else -1
        if at == -1:
            logger.warning("Spoken words not found in paragraph: %r", words[:60])
            continue
        if _inside_quotes(paragraph, at):
            start = at + len(words)
            continue
        end = at + len(words)
        paragraph = f"{paragraph[:at]}{OPEN}{words}{CLOSE}{paragraph[end:]}"
        start = end + 2
    return paragraph


def _inside_quotes(paragraph: str, at: int) -> bool:
    before = paragraph[:at]
    return before.count(OPEN) > before.count(CLOSE) or before.count('"') % 2 == 1
