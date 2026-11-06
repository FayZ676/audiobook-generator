from tta_script.cast import Cast, Voice
from tta_script.script import Script
from tta_script.character.extract import update_cast
from tta_script.dialogue.extract import get_text_segments, label_script
from tta_script.dialogue.recheck import recheck_script
from tta_script.dialogue.unmarked import mark_spoken_lines


def build_script(text: str, cast: Cast, voices: list[Voice]) -> tuple[Script, Cast]:
    """Turn one chapter into a script. Its least confident lines get a
    second opinion from a stronger model (recheck_speaker_id).

    cast is everyone known from earlier chapters (empty for the first). The
    returned cast adds this chapter's new characters and names; save it and
    pass it with the next chapter so every character keeps one id and voice.

    Callers must not build two chapters of one book at the same time: each
    would start from the same cast and the second save would drop the first
    one's new characters."""
    text = mark_spoken_lines(text)
    cast = update_cast(text, cast, voices)
    script = label_script(get_text_segments(text), cast)
    return recheck_script(script, cast), cast
