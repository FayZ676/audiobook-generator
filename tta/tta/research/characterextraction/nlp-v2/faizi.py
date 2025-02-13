from tta.ner import extract_entities, extract_pos
from tta.text_handler import remove_dialogue


def main(text: str):
    paragraphs = text.split("\n\n")
    paragraphs = [p for p in paragraphs if '"' not in p]
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    names = []
    for paragraph in paragraphs:
        persons = extract_entities(paragraph, ["PERSON"])
        # TODO: Look adjacent to the name for verbs using extract_pos function
        # 1. Parse text surrounding each person (2 words before and 2 words after) as a new string.
        # 2. Call extract_pos on the surrounding string.
        # 3. Check if any of the results are verbs.
        # 4. If verbs, add the name to names.
    return names
