import re

from tta.ner import extract_entities


def remove_quoted_text(paragraph):
    """Removes text inside quotation marks."""
    return re.sub(r'["\'].*?["\']', "", paragraph)


def extract_speakers(text: str):
    quoted_paragraphs = [p for p in text.split("\n\n") if '"' in p or "'" in p]
    filtered_paragraphs = [remove_quoted_text(p) for p in quoted_paragraphs]
    processed_text = "\n\n".join(filtered_paragraphs)
    entities = extract_entities(processed_text, ["PERSON"])
    speaker_counts = {entity: text.count(entity) for entity in set(entities)}
    return sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True)


if __name__ == "__main__":
    with open("../text/harrypotter-1-3.txt") as f:
        text = f.read()

    result = extract_speakers(text)
    for r in result:
        print(r)
