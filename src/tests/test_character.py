import pytest
from tta.character import Character, map_characters_to_voices

# SHERLOCK_PARAGRAPH = """
# Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview. Our clients were punctual to their appointment, for the clock had just struck ten when Dr. Mortimer was shown up, followed by the young baronet. The latter was a small, alert, dark-eyed man about thirty years of age, very sturdily built, with thick black eyebrows and a strong, pugnacious face. He wore a ruddy-tinted tweed suit and had the weather-beaten appearance of one who has spent most of his time in the open air, and yet there was something in his steady eye and the quiet assurance of his bearing which indicated the gentleman.

# “This is Sir Henry Baskerville,” said Dr. Mortimer.

# “Why, yes,” said he, “and the strange thing is, Mr. Sherlock Holmes, that if my friend here had not proposed coming round to you this morning I should have come on my own account. I understand that you think out little puzzles, and I’ve had one this morning which wants more thinking out than I am able to give it.”

# “Pray take a seat, Sir Henry. Do I understand you to say that you have yourself had some remarkable experience since you arrived in London?”

# “Nothing of much importance, Mr. Holmes. Only a joke, as like as not. It was this letter, if you can call it a letter, which reached me this morning.”
# """


# TODO: Fix this as it isn't working consistently
# def test_save_characters_info():
#     """
#     Test if the character information can be saved to and loaded from a JSON file correctly.
#     """
#     characters_info = identify_characters(SHERLOCK_PARAGRAPH)
#     print(characters_info)
#     expected_characters: list[Character] = [
#         Character(name="Sherlock Holmes", age="middle-aged", gender="male"),
#         Character(name="Dr. Mortimer", age="middle-aged", gender="male"),
#         Character(name="Sir Henry Baskerville", age="young adult", gender="male"),
#     ]
#     assert characters_info == expected_characters

@pytest.fixture
def characters():
    return [
        Character(name="Alice", age="young-adult", gender="female"),
        Character(name="Bob", age="middle-aged", gender="male"),
        Character(name="Charlie", age="child", gender="male"),
    ]
# Test the mapping of characters to voices
def test_map_characters_to_voices(characters):
    voiced_characters = map_characters_to_voices(characters)

    # Check if the length of voiced_characters matches the input characters
    assert len(voiced_characters) == len(characters)

    # Verify the assigned voices
    for voiced in voiced_characters:
        assert voiced.character in characters
        assert voiced.voice.age_group == voiced.character.age
        assert voiced.voice.gender == voiced.character.gender

# Test case for when there are not enough voices
def test_no_available_voice_for_character():
    # Create a character that does not match any available voices
    test_characters = [Character(name="Unknown", age="elderly", gender="non-binary")]

    with pytest.raises(ValueError, match="No available voices for Unknown with age elderly and gender non-binary"):
        map_characters_to_voices(test_characters)

# Test case to ensure that all voices are assigned only once
def test_voice_uniqueness():
    test_characters = [
        Character(name="Alice", age="young-adult", gender="female"),
        Character(name="Bob", age="young-adult", gender="male"),
        Character(name="Charlie", age="middle-aged", gender="male"),
    ]

    voiced_characters = map_characters_to_voices(test_characters)

    # Collect assigned voices
    assigned_voices = {voiced.voice.id for voiced in voiced_characters}

    # Ensure all voices are unique
    assert len(assigned_voices) == len(voiced_characters)
