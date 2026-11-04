from string import Template


characters = Template(
    """
<text>
$text
</text>

<known_characters>
$known_characters
</known_characters>

## Instructions
List every character who speaks aloud in the <text>, meaning they have at least one line of dialogue. For each character give:
- names: every name the <text> uses for them, such as "Mr. Dursley" and "Uncle Vernon". Put the fullest name first.
- age: "young" (a child or teenager), "middle-aged" (an adult who is not elderly), or "old" (clearly or explicitly elderly).
- gender: "male" or "female".

## Rules
- Only list characters who speak. Leave out characters who are only mentioned or described.
- Only list characters the <text> names. Leave out unnamed speakers such as "the old man" or "the keeper".
- Leave out every character in <known_characters>, even when the <text> calls them by a different name, title, or nickname.
- Never list a narrator.
"""
)
