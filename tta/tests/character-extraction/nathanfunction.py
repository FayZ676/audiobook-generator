import json
import re

import spacy
from sklearn.metrics import precision_score, recall_score

from tta.models.text import generate_text

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


# Normalize names for consistency
def normalize_names(names):
    return [name.lower().strip() for name in names]


# Clean the LLM response to extract only the list of names
def clean_llm_response(response):
    match = re.search(r"\[.*\]", response, re.DOTALL)
    if match:
        return match.group(0)
    return "[]"


# Test extracted results against True Positives list for precision and recall
def test_precision_recall(predicted, true_positives):
    predicted = normalize_names(predicted)
    true_positives = normalize_names(true_positives)
    all_names = list(set(true_positives + predicted))
    y_true = [1 if name in predicted else 0 for name in all_names]
    y_pred = [1 if name in true_positives else 0 for name in all_names]

    precision = precision_score(y_true, y_pred, zero_division=1)
    recall = recall_score(y_true, y_pred, zero_division=1)
    return precision, recall


if __name__ == "__main__":
    with open("../text/harrypotter-1-3.txt") as f:
        text = f.read()
    entities = ner_extraction(text)
    llm_prompt_text = llm_prompt(entities, text)
    extracted_speakers = generate_text(
        "", llm_prompt_text, response_format={"type": "text"}
    )
    cleaned_response = clean_llm_response(extracted_speakers)
    try:
        extracted_speakers_list = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        extracted_speakers_list = []
    true_positives = [
        "Professor McGonagall",
        "Dumbledore",
        "Mrs. Dursley",
        "Mr. Dursley",
    ]

    precision, recall = test_precision_recall(extracted_speakers_list, true_positives)

    print("Extracted Entities:", entities)
    print("Extracted Speakers:", extracted_speakers_list)
    print("Precision:", precision)
    print("Recall:", recall)
