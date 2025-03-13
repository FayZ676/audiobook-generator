from string import Template

speakers = Template(
    """
<text>
$text
</text>

<known_speakers>
$known_characters
<known_speakers/>

Analyze the above <text> and identify the speaking characters.
Include their age (young, middle-aged, or elder), and their gender (male, or female).
Keep the spelling of names consistent with the <known_speakers> where relevant.
"""
)


alias = Template(
    """
<text>
$text
</text>

<names>
$names
</names>

## Instructions
Analyze the above <text> and <names> and determine whether any names are aliases for one another. Aliases are different names that refer to the same character. Either categorize aliased names together or keep individual names as distinct names.

## Restrictions
All names in <names> must be accounted for and only those names. You are forbidden from including any other names.

## Response Format
Your response must conform to the following format:
[
    ["Name 1", "Name 2"],  # Name with two aliases.
    ["Name 1", "Name 2", "Name 3"],  # Name with three aliases.
    ["Name 1"],  # Name with no aliases.
    ...
]
"""
)


ages = Template(
    """
<text>
$text
</text>

<characters>
$characters
</characters>

## Instructions
Use the above <text> to identify the age group that each character in <characters> falls into. The options are "young", "middle-aged", or "old".

## Age Group Definitions
"young" is anyone considered a child to teenager.
"middle-aged" is anyone between older than a teenager but younger than an elderly person.
"old" is anyone clearly or explicitly an elderly person.

Return the age group for the characters in the same order that they appear in <characters>.

## Response Format
Your response must conform to the following JSON format:
{
    ages: ["young", "middle-aged", "old", ...]
}
"""
)

genders = Template(
    """
<text>
$text
</text>

<characters>
$characters
</characters>

## Instructions
Use the above <text> to identify the gender group that each character in <characters> falls into. The options are either "male", "female".

Return the gender group for the characters in the exact same order that they appear in <characters>.

## Response Format
Your response must conform to the following JSON format:
{
    genders: ["male", "female, ...]
}
"""
)
