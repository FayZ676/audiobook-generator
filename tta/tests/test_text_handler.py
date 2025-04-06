from tta.text_utils import get_chunks, remove_dialogue


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
    assert remove_dialogue(text) == 'Dumbledore said, "<speech>"'

def test_remove_multiple_dialogues():
    text = '"It does not do to dwell on dreams," Dumbledore said. "and forget to live."'
    assert remove_dialogue(text) == '"<speech>" Dumbledore said. "<speech>"'

def test_remove_mixed_quotes():
    text = "Snape whispered, 'Always.' and turned away."
    # Current implementation doesn't handle single quotes - so expect no change
    assert remove_dialogue(text) == "Snape whispered, 'Always.' and turned away."

def test_remove_nested_quotes():
    text = """Harry said, "Hagrid told me, 'You're a wizard, Harry!'" """
    assert remove_dialogue(text) == 'Harry said, "<speech>" '

def test_remove_quotes_with_punctuation():
    text = 'Voldemort hissed, "There is no good and evil, only power."'
    assert remove_dialogue(text) == 'Voldemort hissed, "<speech>"'

def test_remove_empty_quotes():
    text = 'Hermione said, ""'
    assert remove_dialogue(text) == 'Hermione said, "<speech>"'

def test_remove_dialogue_with_newlines():
    text = 'Ron said, "Bloody hell!"\nHarry replied, "Brilliant!"'
    assert remove_dialogue(text) == 'Ron said, "<speech>"\nHarry replied, "<speech>"'
