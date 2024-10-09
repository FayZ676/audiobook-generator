# from tta.character import identify_characters, Character


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
