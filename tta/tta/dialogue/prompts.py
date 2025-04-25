from string import Template


label_prompt = Template(
    """
## Text
$text
                          
## Speakers
$speakers
                          
## Instructions
Carefully review the Text and label each of the dialogue segments with the appropriate speaker name from the list of Speakers, or the string "Narrator". Use context clues and surrounding segments to correctly identify the Speaker.

## Rules
- All segments prefixed with "N" (for Narrator) should ALWAYS be labeled as "Narrator".
- All segments prefixed with "D" (for Dialogue) should either be labeled with one of the speakers from the list of Speakers, or labeled with "Narrator" if the speaker is not in the list or ambiguous. Only use the string "Narrator" in the amibiguous instances. No other strings are allowed.
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
