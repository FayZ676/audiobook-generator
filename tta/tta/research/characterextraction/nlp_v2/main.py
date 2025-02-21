import re
from tta.ner import extract_entities, is_pos
from tta.text_handler import remove_dialogue

def main(text: str):
    paragraphs = text.split("\n\n")
    paragraphs = [p for p in paragraphs if '"' not in p] #TODO: Investigate why we find "Harold". In a paragrapgh with no quotations
    paragraphs = [remove_dialogue(p) for p in paragraphs]
    names = []
    for paragraph in paragraphs:
        persons = extract_entities(paragraph, ["PERSON"])
        print(f"Extracted persons: {persons}")  #FOR SEEING RESULTS CAN BE DELETED
        for person in persons:
            # USING REGULAR EXPRESSIONS SO THIS WORKS WITH COMPARE.PY
            # TODO: Use Start and end for person entity *See extract_entities* 
            match = re.search(r'\b' + re.escape(person.text) + r'\b', paragraph) 
            if match:
                start_index = match.start()
                end_index = match.end()
                surrounding_text = paragraph[max(0, start_index - 20):end_index + 20] #20 is an arbitrary number for characters before and after PERSON
                print(f"Surrounding text for '{person.text}': {surrounding_text}")  #FOR SEEING RESULTS CAN BE DELETED
                if is_pos(surrounding_text, "VERB"):
                    print(f"Found verb near '{person.text}'")  #FOR SEEING RESULTS CAN BE DELETED
                    names.append(person.text)
    return set(names)

if __name__ == "__main__": #FOR SEEING RESULTS CAN BE DELETED
    with open("c:/Users/Nathan/audiobook-generator-1/tta/tests/text/harrypotter-1.txt", encoding="utf-8") as f:
        text = f.read()
    
    result = main(text)
    print(result)