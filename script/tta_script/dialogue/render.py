"""How segments and speakers are shown to a model."""

from tta_script.cast import NARRATOR_ID, Cast, CastMember


def render_segments(lines: dict[int, str], paragraphs: dict[int, int]) -> str:
    """Number each segment, with a blank line wherever a paragraph ends."""
    rendered: list[str] = []
    for i, line in lines.items():
        if rendered and paragraphs[i] != paragraphs[i - 1]:
            rendered.append("")
        rendered.append(f"{i}. {line}")
    return "\n".join(rendered)


def render_speakers(cast: Cast) -> str:
    return "\n".join(f"- {m.id}: {', '.join(m.names)}" for m in speaker_order(cast))


def speaker_order(cast: Cast) -> list[CastMember]:
    """Narrator first, then c1, c2, ... in a stable order, so prompts repeat
    exactly and can be cached."""

    def key(member: CastMember) -> tuple[int, str]:
        if member.id == NARRATOR_ID:
            return (0, "")
        return (1, member.id[1:].zfill(6))

    return sorted(cast.members, key=key)
