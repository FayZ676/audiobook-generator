import sys
import os
import json
import unittest
from typing import List

# Add the src directory to the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))

print(f"Adding {src_path} to sys.path")  # Debugging line to check the path
sys.path.insert(0, src_path) 

from tta.character import identify_characters, Character

class TestIdentifyCharacters(unittest.TestCase):
    def setUp(self):
        # Sample text for testing
        self.text = """
        Our breakfast table was cleared early, and Holmes waited in his dressing-gown for the promised interview. Our clients were punctual to their appointment, for the clock had just struck ten when Dr. Mortimer was shown up, followed by the young baronet. The latter was a small, alert, dark-eyed man about thirty years of age, very sturdily built, with thick black eyebrows and a strong, pugnacious face. He wore a ruddy-tinted tweed suit and had the weather-beaten appearance of one who has spent most of his time in the open air, and yet there was something in his steady eye and the quiet assurance of his bearing which indicated the gentleman.

        “This is Sir Henry Baskerville,” said Dr. Mortimer.

        “Why, yes,” said he, “and the strange thing is, Mr. Sherlock Holmes, that if my friend here had not proposed coming round to you this morning I should have come on my own account. I understand that you think out little puzzles, and I’ve had one this morning which wants more thinking out than I am able to give it.”

        “Pray take a seat, Sir Henry. Do I understand you to say that you have yourself had some remarkable experience since you arrived in London?”

        “Nothing of much importance, Mr. Holmes. Only a joke, as like as not. It was this letter, if you can call it a letter, which reached me this morning.”
        """

    def test_identify_characters(self):
        """
        Test if the identify_characters function returns a list of Character instances.
        """
        characters_info = identify_characters(self.text)
        self.assertIsInstance(characters_info, List)
        self.assertTrue(all(isinstance(char, Character) for char in characters_info))

    def test_save_characters_info(self):
        """
        Test if the character information can be saved to and loaded from a JSON file correctly.
        """
        characters_info = identify_characters(self.text)
        output_file = 'characters_info.json'
        with open(output_file, 'w') as f:
            json.dump([char.__dict__ for char in characters_info], f)
        
        with open(output_file, 'r') as f:
            loaded_info = json.load(f)
        
        self.assertEqual([char.__dict__ for char in characters_info], loaded_info)

    def test_expected_characters(self):
        """
        Test if all expected characters are found in the text.
        """
        expected_characters = ["Sherlock Holmes", "Dr. Mortimer", "Sir Henry Baskerville"]
        characters_info = identify_characters(self.text)
        found_characters = [char.name for char in characters_info]
        
        for expected_character in expected_characters:
            self.assertIn(expected_character, found_characters)

if __name__ == '__main__':
    unittest.main()
