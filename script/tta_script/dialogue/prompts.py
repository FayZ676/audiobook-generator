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
$speakers

## Instructions
Carefully review the Text and label each of the dialogue segments with the appropriate speaker name from the list of Speakers, or the string "Narrator". Use context clues and surrounding segments to correctly identify the Speaker.

Fiction starts a new paragraph when the speaker changes, so use the paragraph breaks:
- Dialogue segments in the same paragraph almost always belong to the same speaker, including dialogue that continues after an attribution such as "said Mr. Dursley".
- When two characters talk back and forth without attributions, consecutive paragraphs of dialogue alternate between them.

## Rules
- All segments prefixed with "N" (for Narrator) should ALWAYS be labeled as "Narrator".
- All segments prefixed with "D" (for Dialogue) should either be labeled with one of the speakers from the list of Speakers, or labeled with "Narrator" if the speaker is not in the list or ambiguous. Only use the string "Narrator" in the amibiguous instances. No other strings are allowed.
- A "D" segment that is not spoken aloud, such as a word or name being mentioned or emphasised (he had heard the name "Potter"), is labeled "Narrator".
- Strictly preserve the order and index values of the segments in your response.

## Response Format
Your response must conform to the following JSON format:
dialogue: [
    {"index": index value, "speaker": "Speaker Name" or "Narrator"),
    {"index": index value, "speaker": "Speaker Name" or "Narrator"),
    ...
]
"""
)
