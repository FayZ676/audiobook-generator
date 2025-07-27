import re


def normalize_quotes(text: str) -> str:
    """Convert curly quotes to straight quotes for consistent processing."""
    return text.replace("\u201c", '"').replace("\u201d", '"')


HONORIFICS = [
    "Dr",
    "Dr.",
    "Mr",
    "Mr.",
    "Ms",
    "Ms.",
    "Mrs.",
    "Uncle",
    "Aunt",
    "Professor",
]


def get_chunks(text: str, max_words: int) -> list[str]:
    """Split the text into a list chunks each with up to max_words number of words."""

    if not text:
        return [""]

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current_chunk = []
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


def remove_dialogue(text: str) -> str:
    normalized_text = normalize_quotes(text)
    return re.sub(r'"[^"]*"', '"<speech>"', normalized_text)


def reduce_names(names: set[str]):
    names_set = set(names)
    to_remove = set()
    for name in names_set:
        parts = name.split()
        if len(parts) == 1:
            for full_name in names_set:
                if name != full_name and name in full_name.split():
                    to_remove.add(name)
                    break
    return names_set - to_remove


def near_quotes(name: str, text: str):
    normalized_text = normalize_quotes(text)
    name_parts = [part for part in name.split() if part not in HONORIFICS]
    for part in name_parts:
        start_pos = 0
        window_size = 20
        while start_pos < len(normalized_text):
            name_pos = normalized_text.find(part, start_pos)
            if name_pos == -1:
                break
            window_start = max(0, name_pos - window_size)
            window_end = min(len(normalized_text), name_pos + len(part) + window_size)
            window = normalized_text[window_start:window_end]
            if '"' in window:
                return True
            start_pos = name_pos + len(part)
    return False
