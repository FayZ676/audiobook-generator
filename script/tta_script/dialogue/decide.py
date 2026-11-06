"""Label speakers with a decision model: one choice question per dialogue
segment, with the whole chapter as shared evidence, and a confidence per answer."""

from tta_types.cast import NARRATOR_ID, Cast
from tta_script.dialogue.render import render_segments, render_speakers, speaker_order
from tta_script.dialogue.types import TextSegment
from tta_script.models.decisions import Choice, Question, decide


DECISIONS_PREFIX = "openai-decisions:"

GUIDANCE = """\
## How to tell who is speaking
Segments marked (N) are narration and (D) are dialogue. A blank line separates paragraphs.
- Fiction starts a new paragraph when the speaker changes. Dialogue in the same paragraph \
almost always belongs to the same speaker, including dialogue that continues after an \
attribution such as "said Mr. Dursley".
- When two characters talk back and forth without attributions, consecutive paragraphs of \
dialogue alternate between them.
- A (D) segment that is not spoken aloud, such as a word or name being mentioned or \
emphasised (he had heard the name "Potter"), belongs to the narrator.
- Dialogue from a speaker who isn't in the list, or can't be identified, belongs to the narrator."""


def decide_speakers(
    segments: list[TextSegment], cast: Cast, model: str
) -> tuple[dict[int, str], dict[int, float]]:
    """Returns (index -> cast member id, index -> confidence) for dialogue segments."""
    evidence = "\n\n".join(
        [
            "## Speakers\n" + render_speakers(cast),
            GUIDANCE,
            "## Chapter\n"
            + render_segments(
                {i: str(s) for i, s in enumerate(segments)},
                {i: s.paragraph for i, s in enumerate(segments)},
            ),
        ]
    )
    choices = tuple(
        Choice(
            value=m.id,
            description=(
                "The narrator: narration, words not spoken aloud, or a speaker who "
                "isn't listed or can't be identified"
                if m.id == NARRATOR_ID
                else ", ".join(m.names)
            ),
        )
        for m in speaker_order(cast)
    )
    questions = [
        Question(
            name=f"s{i}",
            instructions=f'Who speaks segment {i} of the chapter: "{s.text}"?',
            choices=choices,
        )
        for i, s in enumerate(segments)
        if s.is_dialogue
    ]

    labels: dict[int, str] = {}
    confidence: dict[int, float] = {}
    for name, answer in decide(model, evidence, questions).items():
        i = int(name[1:])
        labels[i] = answer.choice or NARRATOR_ID
        confidence[i] = answer.confidence
    return labels, confidence
