from tta.ner import extract_entities, is_pos
from tta.text_handler import remove_dialogue


def main(text: str) -> set[str]:
    paragraphs = text.split("\n\n")
    paragraphs = [
        p for p in paragraphs if '"' not in p
    ]  # TODO: Investigate why we find "Harold" and "Petunia". In a paragrapgh with no quotations
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    char_window = 20
    names = []
    for paragraph in paragraphs:
        persons = extract_entities(paragraph, ["PERSON"])
        for person in persons:
            start_index = person.start_char
            end_index = person.end_char
            surrounding_text = paragraph[
                max(0, start_index - char_window) : end_index + char_window
            ]
            if is_pos(surrounding_text, "VERB"):
                names.append(person.text)
    return set(names)
