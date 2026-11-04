
QUOTE_VARIANTS = {'"': ["\u201c", "\u201d"]}


# TODO: What are preprocessing steps do we need to run on the text?
def normalize_quotes(text: str) -> str:
    """Convert curly quotes to straight quotes for consistent processing."""
    for target_quote, variants in QUOTE_VARIANTS.items():
        for variant in variants:
            if variant in text:
                text = text.replace(variant, target_quote)
    return text


def get_chunks(text: str, max_words: int) -> list[str]:
    """Split the text into a list chunks each with up to max_words number of words."""

    if not text:
        return [""]

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_word_count = 0

    for paragraph in paragraphs:
        words = paragraph.split()
        paragraph_word_count = len(words)

        if current_word_count + paragraph_word_count <= max_words:
            if current_chunk:
                current_chunk.append(paragraph)
                current_word_count += paragraph_word_count
            else:
                current_chunk = [paragraph]
                current_word_count = paragraph_word_count
        else:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [paragraph]
            current_word_count = paragraph_word_count

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks
