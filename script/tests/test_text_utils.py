from tta_script.text_utils import get_chunks, remove_dialogue, normalize_quotes, near_quotes


def test_basic_text_splitting():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    chunks = get_chunks(text, max_words=4)
    assert len(chunks) == 2
    assert chunks[0] == "First paragraph.\n\nSecond paragraph."
    assert chunks[1] == "Third paragraph."


def test_empty_text():
    text = ""
    chunks = get_chunks(text, max_words=10)
    assert len(chunks) == 1


def test_single_paragraph():
    text = "This is a single paragraph test."
    chunks = get_chunks(text, max_words=10)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_large_paragraphs():
    text = "One two three four.\n\nFive six seven eight.\n\nNine ten eleven twelve."
    chunks = get_chunks(text, max_words=6)
    assert len(chunks) == 3
    assert chunks[0] == "One two three four."
    assert chunks[1] == "Five six seven eight."
    assert chunks[2] == "Nine ten eleven twelve."


def test_remove_dialogue_basic():
    text = 'Dumbledore said, "Happiness can be found even in the darkest of times."'
    assert remove_dialogue(text) == "Dumbledore said,"


def test_remove_multiple_dialogues():
    text = '"It does not do to dwell on dreams," Dumbledore said. "and forget to live."'
    assert remove_dialogue(text) == "Dumbledore said."


def test_remove_mixed_quotes():
    text = "Snape whispered, 'Always.' and turned away."
    assert remove_dialogue(text) == "Snape whispered, and turned away."


def test_remove_nested_quotes():
    text = """Harry said, "Hagrid told me, 'You're a wizard, Harry!'" """
    assert remove_dialogue(text) == "Harry said,"


def test_remove_quotes_with_punctuation():
    text = 'Voldemort hissed, "There is no good and evil, only power."'
    assert remove_dialogue(text) == "Voldemort hissed,"


def test_remove_empty_quotes():
    text = 'Hermione said, ""'
    assert remove_dialogue(text) == "Hermione said,"


def test_remove_dialogue_with_newlines():
    text = 'Ron said, "Bloody hell!"\nHarry replied, "Brilliant!"'
    assert remove_dialogue(text) == "Ron said, Harry replied,"


def test_normalize_quotes():
    # Test curly quotes to straight quotes conversion
    text_with_curly = "\u201cHello,\u201d she said, \u201chow are you?\u201d"
    expected = '"Hello," she said, "how are you?"'
    assert normalize_quotes(text_with_curly) == expected


def test_normalize_quotes_mixed():
    # Test mixed quotes - left curly, right straight
    text_mixed = '\u201cHello," she said, "how are you?"'
    expected = '"Hello," she said, "how are you?"'
    assert normalize_quotes(text_mixed) == expected


def test_remove_dialogue_with_curly_quotes():
    # Test that remove_dialogue works with curly quotes after normalization
    text_with_curly = '\u201cHello,\u201d she said, \u201chow are you?\u201d'
    text_with_straight = '"Hello," she said, "how are you?"'
    result_curly = remove_dialogue(text_with_curly)
    result_straight = remove_dialogue(text_with_straight)
    assert result_curly == result_straight
    assert '"<speech>"' in result_curly


def test_near_quotes_with_curly_quotes():
    # Test that near_quotes detects names near curly quotes
    text_with_curly = '\u201cListen,\u201d Eleanor said, \u201cI didn\'t do it.\u201d'
    text_with_straight = '"Listen," Eleanor said, "I didn\'t do it."'
    assert near_quotes("Eleanor", text_with_curly) == True
    assert near_quotes("Eleanor", text_with_straight) == True
    assert near_quotes("Eleanor", text_with_curly) == near_quotes("Eleanor", text_with_straight)
