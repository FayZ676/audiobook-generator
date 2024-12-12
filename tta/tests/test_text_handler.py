from tta.text_handler import get_chunks


def test_basic_text_splitting():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    chunks = get_chunks(text, chunk_size=4)
    assert len(chunks) == 2
    assert chunks[0] == "First paragraph.\n\nSecond paragraph."
    assert chunks[1] == "Third paragraph."


def test_empty_text():
    text = ""
    chunks = get_chunks(text, chunk_size=10)
    assert len(chunks) == 1


def test_single_paragraph():
    text = "This is a single paragraph test."
    chunks = get_chunks(text, chunk_size=10)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_large_paragraphs():
    text = "One two three four.\n\nFive six seven eight.\n\nNine ten eleven twelve."
    chunks = get_chunks(text, chunk_size=6)
    assert len(chunks) == 3
    assert chunks[0] == "One two three four."
    assert chunks[1] == "Five six seven eight."
    assert chunks[2] == "Nine ten eleven twelve."
