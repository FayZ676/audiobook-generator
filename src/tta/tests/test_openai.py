import pytest
from unittest.mock import patch
from main import generate_text  # Import the function to be tested

def test_generate_text():
    with patch("openai.ChatCompletion.create") as mock_create:
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
        assert result == "This is a test response."
