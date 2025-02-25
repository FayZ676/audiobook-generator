from tta.ner import NER
from tta.text_handler import remove_dialogue


def main(text: str) -> set[str]:
    paragraphs = text.split("\n\n")
    paragraphs = [
        p for p in paragraphs if '"' not in p
    ]  # TODO: Investigate why we find "Harold" and "Petunia". In a paragrapgh with no quotations
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    ner = NER()
    names = set()
    for paragraph in paragraphs:
        names.update(ner.find_names(paragraph))
    return names
