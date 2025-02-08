import re

from tta.ner import extract_entities


def main(text: str, count: int = 20):
    quoted_paragraphs = [p for p in text.split("\n\n") if '"' in p]
    text_unquoted = "\n\n".join(
        [re.sub(r'["\'].*?["\']', "", p) for p in quoted_paragraphs]
    )
    speaker_counts = {
        entity: text.count(entity)
        for entity in extract_entities(text_unquoted, ["PERSON"])
    }
    return {speaker for speaker, freq in speaker_counts.items() if freq > count}
