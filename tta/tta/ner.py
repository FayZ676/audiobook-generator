import spacy


nlp = spacy.load("en_core_web_sm")


def extract_entities(text: str, entities: list[str]):
    doc = nlp(text)
    return {ent.text for ent in doc.ents if ent.label_ in entities}
