from string import Template


label_prompt = Template("""
<text>
$text
</text>
                          
<speakers>
$speakers
</speakers>
                          
## Instructions
Review the above <text> provided and do the following:
1. Identify segments of dialogue (prefixed with 'D').
2. For dialogue segments (prefixed with 'D') attribute the speaker using the list of <speakers> provided.
                          
## Response Format
{
    dialogue: [
        {
            "index": 0,
            "speaker": "Speaker Name"               
        },
        ...
    ]
}
""")
