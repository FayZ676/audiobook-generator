from tta.models.script import convert_text_to_script, Script, Speech


BOOK_PARAGRAPH = """
Sherlock Holmes took a deep breath and began, "It was elementary, my dear Watson."
Watson replied, "You never fail to amaze me, Holmes."
"""


def test_convert_text_to_script():
    """
    Test if the text is correctly converted into a structured Script with speeches.
    """
    # Generate the script from the paragraph
    script_result = convert_text_to_script(BOOK_PARAGRAPH)
    
    # Expected structured script with Speech objects
    expected_script = Script(
        speeches=[
            Speech(speaker="Sherlock Holmes", text="It was elementary, my dear Watson."),
            Speech(speaker="Watson", text="You never fail to amaze me, Holmes.")
        ]
    )
    
    # Assert the result is the same as expected
    assert script_result == expected_script


if __name__ == "__main__":
    test_convert_text_to_script()
    print("Test passed!")