from tta.models.script import generate_script_from_text

def test_generate_script_returns_str():
    book_text = "Once upon a time, there was a dragon."
    script_output = generate_script_from_text(book_text)
    
    # Check if the output is a string
    assert isinstance(script_output, str), "The result should be of type string."
