from collections import Counter

from tta.ner import NER
from tta.text_handler import remove_dialogue


def main(text: str, threshold: int) -> set[str]:
    paragraphs = [
        p for p in text.split("\n\n") if '"' not in p
    ]  # TODO: Investigate why we find "Harold" and "Petunia". In a paragrapgh with no quotations
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    ner = NER()
    name_counter = Counter()
    for paragraph in paragraphs:
        names = ner.find_names(paragraph)
        name_counter.update(names)
    return {name for name, count in name_counter.items() if count > threshold}
