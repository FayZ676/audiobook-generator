import json
import re

import spacy

from tta.models.text import generate_text
from tta.metrics import test_precision_recall

nlp = spacy.load("en_core_web_sm")  # install en_core_web_trf


def ner_extraction(text):
    doc = nlp(text)
    entities = {ent.text for ent in doc.ents if ent.label_ == "PERSON"}
    return entities


def llm_prompt(entities_list, text):
    prompt = f"""
    System: You are an expert in literature and NLP.
    User: Here is a list of entities found by NER: {entities_list}. These names are just suggestions and not necessarily true.
    We are looking specifically for the names of characters that are speakers, i.e., they say something in the text, typically with quotation marks.
    Please combine names that refer to the same character and identify them as one character using the most commonly used name, for example if a character is referred to by their first and last name, or just their first or last name, identify them as by the name used most often, keep a count of name occurances to help identify the main name of each character. Only return the names in a Python list format, like this: ["Name1", "Name2", "Name3"]
    Here is the text: {text}
    """
    return prompt


# Clean the LLM response to extract only the list of names
def clean_llm_response(response):
    match = re.search(r"\[.*\]", response, re.DOTALL)
    if match:
        return match.group(0)
    return "[]"


if __name__ == "__main__":
    with open("../text/harrypotter-1-3.txt") as f:
        text = f.read()

    entities = ner_extraction(text)

    extracted = generate_text(
        "", llm_prompt(entities, text), response_format={"type": "text"}
    )
    extracted_speakers_list = json.loads(clean_llm_response(extracted))
    expected = [
        "Professor McGonagall",
        "Dumbledore",
        "Mrs. Dursley",
        "Mr. Dursley",
    ]

    precision, recall = test_precision_recall(extracted_speakers_list, expected)

    print("Extracted Entities:", entities)
    print("Extracted Speakers:", extracted_speakers_list)
    print("Precision:", precision)
    print("Recall:", recall)
