import re


def get_chunks(text: str, chunk_size: int) -> list[str]:
    if not text:
        return [""]

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current_chunk = []
    current_word_count = 0

    for paragraph in paragraphs:
        words = paragraph.split()
        paragraph_word_count = len(words)

        if current_word_count + paragraph_word_count <= chunk_size:
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
    return re.sub(r'"[^"]*"', '"<speech>"', text)


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
    start_pos = 0
    window_size = 20
    while start_pos < len(text):
        name_pos = text.find(name, start_pos)
        if name_pos == -1:
            return False
        window_start = max(0, name_pos - window_size)
        window_end = min(len(text), name_pos + len(name) + window_size)
        window = text[window_start:window_end]
        if '"' in window:
            return True
        start_pos = name_pos + len(name)
    return False
