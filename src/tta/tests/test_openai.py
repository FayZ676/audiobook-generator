import unittest
from unittest.mock import patch
import openai
from main import generate_text  # Import the function to be tested

class TestGenerateText(unittest.TestCase):

    @patch("openai.ChatCompletion.create")
    def test_generate_text(self, mock_create):
        # Define what the mock should return
        mock_create.return_value = {
            "choices": [
                {"message": {"content": "This is a test response."}}
            ]
        }

        # Call the function with a test prompt
        prompt = "Test prompt for GPT"
        result = generate_text(prompt)

        # Assert that the result is as expected
        self.assertEqual(result, "This is a test response.")

if __name__ == "__main__":
    unittest.main()
