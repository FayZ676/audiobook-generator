import re

from tta.ner import extract_entities


def remove_quoted_text(paragraph):
    return re.sub(r'["\'].*?["\']', "", paragraph)


def main(text: str, count: int = 20):
    quoted_paragraphs = [p for p in text.split("\n\n") if '"' in p or "'" in p]
    filtered_paragraphs = [remove_quoted_text(p) for p in quoted_paragraphs]
    processed_text = "\n\n".join(filtered_paragraphs)
    entities = extract_entities(processed_text, ["PERSON"])
    speaker_counts = {entity: text.count(entity) for entity in set(entities)}
    return {speaker for speaker, freq in speaker_counts.items() if freq > count}
