import re

from tta.ner import extract_entities
from tta.text_handler import remove_dialogue


# TODO: Use the remove_dialogue function.
def main(text: str, count: int = 20):
    quoted_paragraphs = [p for p in text.split("\n\n") if '"' in p]
    text_unquoted = "\n\n".join(
        [re.sub(r'["\'].*?["\']', "", p) for p in quoted_paragraphs]
    )
    speaker_counts = {
        entity.text: text.count(entity.text)
        for entity in extract_entities(text_unquoted, ["PERSON"])
    }
    return {speaker for speaker, freq in speaker_counts.items() if freq > count}
