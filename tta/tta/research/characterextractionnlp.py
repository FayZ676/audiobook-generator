from collections import Counter

from tta.ner import NER
from tta.text_handler import remove_dialogue


def resolve_redundancies(names: set[str]):
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


def main(text: str, threshold: int) -> set[str]:
    paragraphs = [
        p for p in text.split("\n\n") if '"' in p
    ]  # TODO: Investigate why we find "Harold" and "Petunia". In a paragrapgh with no quotations
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    ner = NER()
    name_counter = Counter()
    for paragraph in paragraphs:
        names = ner.find_names(paragraph)
        name_counter.update(names)
    return resolve_redundancies(
        {name for name, count in name_counter.items() if count > threshold}
    )
