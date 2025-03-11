from tta.ner import NER
from tta.text_handler import remove_dialogue


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


def main(text: str) -> set[tuple[str]]:
    paragraphs = [
        p.replace("\n", " ")
        for p in text.split("\n\n")
        if p.count('"') % 2 == 0 and p.count('"') > 0
    ]
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    ner = NER()
    names = reduce_names(
        {name for paragraph in paragraphs for name in ner.find_names(paragraph)}
    )
    return {(name,) for name in names if near_quotes(name, "\n\n".join(paragraphs))}
