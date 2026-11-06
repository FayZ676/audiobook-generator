import json
import os
import re
from typing import Literal

from pydantic import BaseModel, create_model

from tta_script.cast import NARRATOR_ID, Cast
from tta_script.script import Script, ScriptSegment
from tta_script.dialogue.prompts import label_prompt
from tta_script.dialogue.types import TextSegment
from tta_script.dialogue.decide import DECISIONS_PREFIX, decide_speakers
from tta_script.dialogue.render import render_segments, render_speakers
from tta_script.models.text import generate_text


# Labels dialogue with OpenAI's Decisions API, which also reports each line's
# confidence. Set TTA_LABEL_MODEL to an LLM ("anthropic:claude-haiku-5-5")
# to label with that instead.
DEFAULT_LABEL_MODEL = "openai-decisions:gpt-6-luna"

BATCH_SIZE = 100
# Narration this short between two quotes in one paragraph is an attribution
# ("said he,", "added the March Hare,"), and both quotes are one speaker's.
MAX_ATTRIBUTION_WORDS = 5
# How many already-labelled segments each batch sees, so a conversation that
# crosses a batch boundary keeps track of who is speaking.
CONTEXT_SIZE = 30


def label_script(segments: list[TextSegment], cast: Cast) -> Script:
    """Turn segments into a script, with every segment pointing at a cast member.

    Narration, and dialogue the model didn't label, is read by the narrator.
    TTA_LABEL_MODEL picks the labeller (default: DEFAULT_LABEL_MODEL). An
    "openai-decisions:<model>" labeller also reports each line's confidence."""
    model = os.getenv("TTA_LABEL_MODEL") or DEFAULT_LABEL_MODEL
    confidence: dict[int, float] = {}
    if model.startswith(DECISIONS_PREFIX):
        labels, confidence = decide_speakers(segments, cast, model.removeprefix(DECISIONS_PREFIX))
    else:
        labels = _llm_labels(segments, cast)
    _keep_speaker_across_attributions(segments, labels, confidence)

    return Script(
        segments=[
            ScriptSegment(
                id=f"seg-{i:04d}",
                text=s.text,
                speaker_id=labels.get(i, NARRATOR_ID) if s.is_dialogue else NARRATOR_ID,
                confidence=confidence.get(i) if s.is_dialogue else None,
            )
            for i, s in enumerate(segments)
        ]
    )


def _keep_speaker_across_attributions(
    segments: list[TextSegment], labels: dict[int, str], confidence: dict[int, float]
) -> None:
    """Give both quotes around a short attribution in one paragraph the same
    speaker: the one the labeller was surer of, or the first without
    confidences. Only two characters are reconciled; a narrator label is
    left alone, since a quote beside an attribution can be words not said
    aloud ("She didn't say "perhaps never"")."""
    for i in range(len(segments) - 2):
        before, between, after = segments[i : i + 3]
        speakers = labels.get(i, NARRATOR_ID), labels.get(i + 2, NARRATOR_ID)
        if not (
            before.is_dialogue
            and after.is_dialogue
            and not between.is_dialogue
            and before.paragraph == between.paragraph == after.paragraph
            and len(between.text.split()) <= MAX_ATTRIBUTION_WORDS
            and NARRATOR_ID not in speakers
            and speakers[0] != speakers[1]
        ):
            continue
        keep, change = (i, i + 2) if confidence.get(i, 1.0) >= confidence.get(i + 2, 0.0) else (i + 2, i)
        labels[change] = labels[keep]
        if keep in confidence:
            confidence[change] = confidence[keep]


def _llm_labels(segments: list[TextSegment], cast: Cast) -> dict[int, str]:
    labels: dict[int, str] = {}
    for start in range(0, len(segments), BATCH_SIZE):
        batch = {i: segments[i] for i in range(start, min(start + BATCH_SIZE, len(segments)))}
        context = {
            i: (segments[i], labels.get(i, NARRATOR_ID))
            for i in range(max(0, start - CONTEXT_SIZE), start)
        }
        labels.update(label(batch, cast, context))
    return labels


def label(
    segments: dict[int, TextSegment],
    cast: Cast,
    context: dict[int, tuple[TextSegment, str]] | None = None,
) -> dict[int, str]:
    """Ask the model who speaks each segment. Returns index -> cast member id."""
    context = context or {}
    prompt = label_prompt.substitute(
        context=render_segments(
            {i: f"{s} -> {speaker}" for i, (s, speaker) in context.items()},
            {i: s.paragraph for i, (s, _) in context.items()},
        )
        or "(start of chapter)",
        text=render_segments(
            {i: str(s) for i, s in segments.items()},
            {i: s.paragraph for i, s in segments.items()},
        ),
        speakers=render_speakers(cast),
    )
    response = generate_text("", prompt, _response_format(cast))
    return {
        label["index"]: label["speaker"]
        for label in json.loads(response)["dialogue"]
        if label["index"] in segments  # ignore labels for context segments
    }


def _response_format(cast: Cast) -> type[BaseModel]:
    """A response model that only accepts ids of this cast."""
    speaker_ids = tuple(m.id for m in cast.members)
    label_model = create_model(
        "DialogueLabel",
        index=(int, ...),
        speaker=(Literal[speaker_ids], ...),  # type: ignore[valid-type]
    )
    return create_model("DialogueLabels", dialogue=(list[label_model], ...))  # type: ignore[valid-type]


OPEN, CLOSE = "\u201c", "\u201d"
# How far ahead to look for the end of a quote left open at a paragraph's end.
MAX_QUOTED_PARAGRAPHS = 3


def get_text_segments(text: str) -> list[TextSegment]:
    """Split a chapter into narration and dialogue segments, in order.

    Paragraphs are separated by blank lines. Double quotes mark dialogue,
    straight or curly, or single quotes in a text that uses them for dialogue
    (British style, with double quotes for a quote inside a quote), or a dash
    opening the paragraph in a text that marks speech that way (\u2014Back to
    barracks! he said sternly.). Quotes inside a quote stay part of it. A quote may run
    over several paragraphs, as a long speech or a song does; it is carried
    into the next paragraph only when a later paragraph shows it continuing,
    so one unclosed quote can't turn the rest of the chapter into dialogue."""
    paragraphs = [" ".join(p.split()) for p in text.split("\n\n") if p.strip()]
    if _uses_dashes(paragraphs):
        return [
            TextSegment(part, is_dialogue, index)
            for index, paragraph in enumerate(paragraphs)
            for part, is_dialogue in _split_dash_paragraph(paragraph)
        ]
    if _uses_single_quotes(text):
        paragraphs = [
            _single_quotes_as_double(p, paragraphs[k + 1 : k + 1 + MAX_QUOTED_PARAGRAPHS])
            for k, p in enumerate(paragraphs)
        ]
    else:
        paragraphs = [_curly_quotes(p) for p in paragraphs]
    segments: list[TextSegment] = []

    def add(segment_text: str, is_dialogue: bool, paragraph: int):
        segment_text = segment_text.translate(_UNHIDE).strip()
        if segment_text:
            segments.append(TextSegment(segment_text, is_dialogue, paragraph))

    depth = 0  # 1 inside a quote, 2+ inside a quote within it
    for index, paragraph in enumerate(paragraphs):
        if depth and paragraph.startswith(OPEN):
            paragraph = paragraph[1:]  # marks a speech continuing from the last paragraph
        current = ""
        opened = depth > 0
        for char in paragraph:
            if char == OPEN and depth == 0:
                add(current, False, index)
                current, depth, opened = "", 1, True
            elif char == CLOSE and depth == 1:
                add(current, True, index)
                current, depth = "", 0
            elif char == CLOSE and depth == 0:
                # A closing quote before any opening one: the paragraph began
                # in dialogue and lost its opening quote. Later ones are strays.
                add(current, not opened, index)
                current, opened = "", True
            else:
                depth += char == OPEN
                depth -= char == CLOSE
                current += char
        add(current, depth > 0, index)
        depth = 1 if depth and _quote_continues(paragraphs[index + 1 :]) else 0
    return segments


def has_dialogue_marks(text: str) -> bool:
    """Whether the text marks speech in a way the splitter reads: double or
    single quotes, or dashes opening paragraphs."""
    paragraphs = [" ".join(p.split()) for p in text.split("\n\n") if p.strip()]
    double_quotes = text.count(OPEN) + text.count('"')
    return double_quotes >= 2 or _uses_single_quotes(text) or _uses_dashes(paragraphs)


def _quote_continues(following: list[str]) -> bool:
    """Whether a quote left open at a paragraph's end carries on into the next."""
    for distance, paragraph in enumerate(following[:MAX_QUOTED_PARAGRAPHS]):
        if distance == 0 and paragraph.startswith(OPEN):
            return True  # the usual way a speech carries on into a new paragraph
        first_open, first_close = paragraph.find(OPEN), paragraph.find(CLOSE)
        if first_close != -1 and (first_open == -1 or first_close < first_open):
            return True
        if first_open != -1:
            return False  # a new quote opens first, so the last one was never closed
    return False


def _curly_quotes(paragraph: str) -> str:
    """Turn straight double quotes into opening and closing ones: a quote
    with text after it and a space or bracket (or nothing) before it opens,
    any other closes."""
    if '"' not in paragraph:
        return paragraph
    paragraph = paragraph.replace("\'\'", '"')  # a typo for a closing quote

    def opens(i: int) -> bool:
        before = paragraph[i - 1] if i else " "
        after = paragraph[i + 1] if i + 1 < len(paragraph) else " "
        return (before.isspace() or before in "([") and not after.isspace()

    return "".join(
        (OPEN if opens(i) else CLOSE) if char == '"' else char for i, char in enumerate(paragraph)
    )


# Where single quotes mark dialogue, double quotes in the text quote something
# inside it or mention a word; they are hidden from the splitter as these
# placeholders, and restored in each segment's text.
_HIDE = str.maketrans({OPEN: "\ue000", CLOSE: "\ue001", '"': "\ue002"})
_UNHIDE = str.maketrans({"\ue000": OPEN, "\ue001": CLOSE, "\ue002": '"'})
# Speech ends with punctuation, or with a quote inside it, so a single quote
# after one of these closes the speech.
SPEECH_END = ".,!?;:-\u2014\u2013\u2026)\ue001\ue002"


def _uses_single_quotes(text: str) -> bool:
    """Whether dialogue is in single quotes. Speech opens many paragraphs,
    while single quotes that only mention a word (the \u2018Mouse\u2019) sit
    inside them, so count the paragraphs each kind of quote opens."""
    openings = [p.lstrip()[:1] for p in text.split("\n\n") if p.strip()]
    singles = sum(o in ("\u2018", "'") for o in openings)
    doubles = sum(o in (OPEN, '"') for o in openings)
    return singles >= 3 and singles > 2 * doubles


def _single_quotes_as_double(paragraph: str, following: list[str]) -> str:
    """Turn the single quotes that mark dialogue into double ones, leaving
    apostrophes (don\u2019t, goin\u2019, \u2019em) alone. Double quotes already in
    the text quote something inside the speech, so they are hidden."""
    paragraph = paragraph.translate(_HIDE)
    marked = []
    in_quote = False
    for i, char in enumerate(paragraph):
        if _opens_single(paragraph, i) and not in_quote and _straight_quote_closes(paragraph, i, following):
            marked.append(OPEN)
            in_quote = True
        elif char in "\u2019'" and not _opens_single(paragraph, i) and _closes_single(paragraph, i, in_quote):
            marked.append(CLOSE)
            in_quote = False
        else:
            marked.append(char)
    return "".join(marked)


def _opens_single(paragraph: str, i: int) -> bool:
    if paragraph[i] == "\u2018":
        return True
    before = paragraph[i - 1] if i else " "
    after = paragraph[i + 1] if i + 1 < len(paragraph) else " "
    return paragraph[i] == "'" and (before.isspace() or before in "([") and not after.isspace()


def _straight_quote_closes(paragraph: str, i: int, following: list[str]) -> bool:
    """A straight quote before a lowercase letter can be an apostrophe (\'tis,
    \'ittle), so it only opens a quote that closes later, in this paragraph or
    one of the following ones. Speech that opens with a capital or a dash
    always opens a quote."""
    if paragraph[i] != "'" or not paragraph[i + 1].islower():
        return True
    for start, text in [(i + 1, paragraph)] + [(0, p) for p in following]:
        for j in range(start, len(text)):
            if _opens_single(text, j):
                if j + 1 < len(text) and not text[j + 1].islower():
                    return False  # a new speech opens before this one closes
            elif text[j] in "\u2019'" and _closes_single(text, j, True):
                return True
    return False


def _closes_single(paragraph: str, i: int, in_quote: bool) -> bool:
    before = paragraph[i - 1] if i else " "
    after = paragraph[i + 1] if i + 1 < len(paragraph) else " "
    if after.isalpha():
        return False  # inside a word: don\u2019t, o\u2019clock
    if before in SPEECH_END:
        return True
    if not in_quote:
        return False  # a word cut short outside any quote: goin\u2019
    # A word cut short inside speech (goin\u2019 home), or the end of a quoted
    # phrase (\u2018true sea-dog\u2019)? It ends the quote unless the speech's own
    # closing quote still comes before any new opening one.
    for j in range(i + 1, len(paragraph)):
        if _opens_single(paragraph, j):
            return True
        if paragraph[j] in "\u2019'" and paragraph[j - 1] in SPEECH_END:
            return False
    return True


DASH = "\u2014"
_ATTRIBUTION_VERBS = (
    "said|says|asked|asks|cried|cries|answered|answers|replied|replies|began|added|adds|"
    "shouted|whispered|murmured|called|laughed|sighed|exclaimed|returned|repeated|continued|"
    "muttered|demanded|inquired|enquired|observed|remarked|declared|went on|broke in|"
    "interrupted|suggested|explained|agreed|protested|chanted|intoned|sang|told"
)
# Who speaks: he/she/they, a capitalised name of up to three words, or "the
# old woman". Capitalised pronouns and "I" are left out: "She asked you" and
# "I said" begin sentences inside speech, while attributions say "he said".
_NAME_WORD = r"(?:(?:Mr|Mrs|Ms|Dr|St)\.|[A-Z][\w\u2019'-]*)"
_SPEAKER = (
    rf"(?:he|she|they|(?!(?:He|She|They|It|We|You|I)\b){_NAME_WORD}(?: {_NAME_WORD}){{0,2}}"
    r"|(?:the|his|her|a|an) [a-z]+(?: [a-z]+)?)"
)
# An attribution follows the speech's punctuation and ends at its own:
# "he said sternly.", "Buck Mulligan said.", "said Stephen,". A participle
# straight after it is still narration: "Stephen said, turning."
_ATTRIBUTION = re.compile(
    rf"(?<=[,.!?;:\u2026])\s+(?:{_SPEAKER} (?:[a-z]+ly )?(?:{_ATTRIBUTION_VERBS})"
    rf"|(?:{_ATTRIBUTION_VERBS}) {_SPEAKER})\b[^.!?,;:]*[.!?,;:]"
    r"(?:\s+[a-z]+ing\b[^.!?,]*[.!?,])?"
)


def _uses_dashes(paragraphs: list[str]) -> bool:
    """Whether speech is marked by a dash opening its paragraph, not quotes."""
    dashed = sum(_opens_with_dash(p) for p in paragraphs)
    quoted = sum(any(mark in p for mark in (OPEN, '"', "\u2018")) for p in paragraphs)
    return dashed >= 3 and dashed > quoted


def _opens_with_dash(paragraph: str) -> bool:
    # "\u2014 I \u2014", a heading, has a space after its dash; speech doesn't.
    return paragraph.startswith(DASH) and len(paragraph) > 1 and not paragraph[1].isspace()


def _split_dash_paragraph(paragraph: str) -> list[tuple[str, bool]]:
    """Split a paragraph into (text, is_dialogue) parts. Speech runs from the
    opening dash to the end of the paragraph, except for attributions."""
    if not _opens_with_dash(paragraph):
        return [(paragraph, False)]
    speech = paragraph[1:]
    parts: list[tuple[str, bool]] = []
    start = 0
    for match in _ATTRIBUTION.finditer(speech):
        parts.append((speech[start : match.start()].strip(), True))
        parts.append((match.group().strip(), False))
        start = match.end()
    parts.append((speech[start:].strip(), True))
    return [(text, is_dialogue) for text, is_dialogue in parts if text]
