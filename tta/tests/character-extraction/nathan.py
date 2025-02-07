import json

import spacy
from pydantic import BaseModel

from tta.models.text import generate_text
from tta.metrics import test_precision_recall


nlp = spacy.load("en_core_web_sm")


class ResponseFormat(BaseModel):
    response: list[str]


# TODO: Move out to tta package in new ner module.
def ner_extraction(text):
    doc = nlp(text)
    entities = {ent.text for ent in doc.ents if ent.label_ == "PERSON"}
    return entities


def llm_prompt(entities_list, text):
    prompt = f"""
    <text>
    {text}
    </text>

    <names>
    {entities_list}
    </names>

    The <names> are just suggestions and not necessarily true.
    We are looking specifically for the names of characters that are speakers, i.e., they say something in the text, typically with quotation marks.
    Please combine names that refer to the same character and identify them as one character using the most commonly used name, for example if a character is referred to by their first and last name, or just their first or last name, identify them as by the name used most often, keep a count of name occurances to help identify the main name of each character. 
    
    Do not include any preamble or postamble text in your response.
    Respond only with a list of names, For example:
    ["Name1", "Name2", "Name3"]
    """
    return prompt


def main(text: str, entities: set[str]) -> set[str]:
    result = generate_text(
        "", llm_prompt(entities, text), response_format=ResponseFormat
    )
    return {name for name in json.loads(result)["response"]}


if __name__ == "__main__":
    with open("../text/harrypotter-1-3.txt") as f:
        text = f.read()

    entities = ner_extraction(text)
    speakers = main(text, entities)
    expected = {
        "Professor McGonagall",
        "Dumbledore",
        "Mrs. Dursley",
        "Mr. Dursley",
    }

    precision, recall = test_precision_recall(speakers, expected)
    print("Extracted Entities:", entities)
    print("Extracted Speakers:", speakers)
    print("Precision:", precision)
    print("Recall:", recall)
