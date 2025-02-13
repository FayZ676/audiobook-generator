from tta.ner import extract_entities, extract_pos
from tta.text_handler import remove_dialogue


def main(text: str):
    paragraphs = text.split("\n\n")
    paragraphs = [p for p in paragraphs if '"' not in p]
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    names = []
    for p in paragraphs:
        persons = extract_entities(p, ["PERSON"])
        # TODO: Look adjacent to the name for verbs using extract_pos function
        # TODO: If verbs, add the name to names.
    return names
