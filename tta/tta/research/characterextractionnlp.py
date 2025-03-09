from tta.ner import NER
from tta.text_handler import remove_dialogue


def main(text: str) -> set[str]:
    paragraphs = [
        p for p in text.split("\n\n") if '"' not in p
    ]  # TODO: Investigate why we find "Harold" and "Petunia". In a paragrapgh with no quotations
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    ner = NER()
    return {name for paragraph in paragraphs for name in ner.find_names(paragraph)}
