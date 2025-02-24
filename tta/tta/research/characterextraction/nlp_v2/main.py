import re
from tta.ner import extract_entities, is_pos
from tta.text_handler import remove_dialogue


def main(text: str) -> set[str]:
    paragraphs = text.split("\n\n")
    paragraphs = [
        p for p in paragraphs if '"' not in p
    ]  # TODO: Investigate why we find "Harold" and "Petunia". In a paragrapgh with no quotations
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    names = []
    for paragraph in paragraphs:
        persons = extract_entities(paragraph, ["PERSON"])
        for person in persons:
            # USING REGULAR EXPRESSIONS SO THIS WORKS WITH COMPARE.PY
            # TODO: Use Start and end for person entity *See extract_entities*
            match = re.search(r"\b" + re.escape(person.text) + r"\b", paragraph)
            if match:
                start_index = match.start()
                end_index = match.end()
                surrounding_text = paragraph[
                    max(0, start_index - 20) : end_index + 20
                ]  # 20 is an arbitrary number for characters before and after PERSON
                if is_pos(surrounding_text, "VERB"):
                    names.append(person.text)
    return set(names)
