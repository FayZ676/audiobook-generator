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
    # Pattern to get content inside single/double quotes
    quote_pattern = r'(["\'])(?:(?=(\\?))\2.)*?\1'

    text_without_dialogue = re.sub(quote_pattern, '', text)

    return ' '.join(text_without_dialogue.split())