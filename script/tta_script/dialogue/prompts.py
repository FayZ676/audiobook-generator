from string import Template


label_prompt = Template(
    """
## Preceding Segments
Already labeled, shown only so you know who was speaking. Do not label these.
$context

## Text
Each segment is numbered. A blank line separates paragraphs.
$text

## Speakers
Each speaker's id, then the names the book uses for them.
$speakers

## Instructions
Label every segment in the Text with the id of its speaker. Use context clues and surrounding segments to identify who is speaking.

Fiction starts a new paragraph when the speaker changes, so use the paragraph breaks:
- Dialogue segments in the same paragraph almost always belong to the same speaker, including dialogue that continues after an attribution such as "said Mr. Dursley".
- When two characters talk back and forth without attributions, consecutive paragraphs of dialogue alternate between them.

## Rules
- Segments marked (N) are narration: always label them "narrator".
- Segments marked (D) are dialogue: label them with the speaker's id, or "narrator" if the speaker isn't in the list or can't be identified.
- A (D) segment that is not spoken aloud, such as a word or name being mentioned or emphasised (he had heard the name "Potter"), is labeled "narrator".
- A (D) segment spoken by several characters together ("No room!" they cried) is labeled "narrator".
- Quoted thoughts, and text a character reads aloud such as a letter, are labeled with that character's id.
- When the narrator has a name, the book is told in the first person by that character: their own spoken lines ("said I") are labeled "narrator".
- Keep each segment's index exactly as given.
"""
)
