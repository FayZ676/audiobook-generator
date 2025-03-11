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


def get_key_names(text: str, names: set[str], threshold: int):
    return {name for name in names if text.count(name) >= threshold}


def main(text: str, threshold: int = 7) -> set[str]:
    paragraphs = [p for p in text.split("\n\n") if '"' in p]
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    ner = NER()
    return resolve_redundancies(
        get_key_names(
            text,
            {name for paragraph in paragraphs for name in ner.find_names(paragraph)},
            threshold,
        )
    )
