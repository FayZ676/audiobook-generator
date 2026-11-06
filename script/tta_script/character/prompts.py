from string import Template


cast_update = Template(
    """
<text>
$text
</text>

<known_characters>
$known_characters
</known_characters>

## Instructions
Find every character who speaks aloud in the <text>, meaning they have at least one line of dialogue.

For a character already in <known_characters>, add them to "known" with their id and any names the <text> uses for them that aren't listed yet, such as a title, first name, or nickname ("Uncle Vernon" for a known "Mr. Dursley"). Use an empty list when there are no new names.

For any other character, add them to "new" with:
- names: every name or description the <text> uses for them. Put the fullest name first.
- age: "young" (a child or teenager), "middle-aged" (an adult who is not elderly), or "old" (clearly or explicitly elderly).
- gender: "male" or "female".

If the <text> is told in the first person by one of its characters ("said I"), put the names the <text> uses for that narrator in "narrator_names", such as "Watson" and "Dr. Watson", and leave them out of "known" and "new": the narrator reads their own lines. Otherwise use an empty list. A known character with the id "narrator" is a first-person narrator found earlier.

## Rules
- Only include characters who speak. Leave out characters who are only mentioned or described.
- Include speakers the <text> only describes, such as "the old man", "Scrooge's nephew" or "the keeper", using that description as their name. Leave out voices that can't be told apart from others, such as "a voice" or "someone".
- Lines several characters speak together don't make a speaker of the group.
- Never put a character from <known_characters> in "new", even when the <text> calls them something different.
- Never put the narrator in "known" or "new".
"""
)
