from string import Template


label_prompt = Template(
    """
## Text
$text
                          
## Speakers
$speakers
                          
## Instructions
Carefully review the Text and label the dialogue segments explicitly prefixed with '(D)' with the appropriate speaker from the list of Speakers. Use context clues and surrounding segments to correctly identify the Speaker.

## Context Clues
- Segments with verbs such as "said", "asked", "replied", etc. often indicate the speaker of the previous segment of dialogue. For example, a segment with "said John" means that the previous segment is spoken by John.

Only label segments explicitly prefixed with 'D'. If a dialogue segment appears to be spoken by a speaker not referenced in the list of Speakers, simply skip it, do not attempt to label it.

There are $num_dialogue segments in total. Hence, return no more than $num_dialogue labels.
                          
## Response Format
Your response must conform to the following JSON format:
{
    dialogue: [
        {
            "index": Segment Index,
            "speaker": "Speaker Name"               
        },
        ...
    ]
}
"""
)
