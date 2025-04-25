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
Keep these rules in mind when identifying the speaker:
- Verbage: Segments with verbs such as "said", "asked", "replied", etc. always indicate the speaker of the segment or preceeding segment(s). For example, a segment with "said John" means that the most recent dialogue segment is spoken by John.
- Conversation Flow: Trust that the speaker will always be referenced by name somewhere in the text. It may not be in the segment itself, or even adjacent segments, but by following the natural flow of the conversation the speaker name will be clear.
- Assumptions: Do not make assumptions about the speaker's identity if it is not explicitly stated in the text. Use the above rules to guide your identification, and only identify the speaker for segments that are clearly indicated.

If a dialogue segment appears to be spoken by a speaker not referenced in the list of Speakers, simply label the speaker with the string "Narrator".

There are $num_segments segments in total. Hence, return exactly $num_segments back.
                          
## Response Format
Your response must conform to the following JSON format:
dialogue: [
    {"index": index value, "speaker": "Speaker Name" or "Narrator"),
    {"index": index value, "speaker": "Speaker Name" or "Narrator"),
    ...
]
"""
)
