import spacy


# TODO: Use en_core_web_trf instead
nlp = spacy.load("en_core_web_sm")


def extract_entities(text: str, entities: list[str]):
    doc = nlp(text)
    return {ent.text for ent in doc.ents if ent.label_ in entities}


# TODO: Implement
def extract_pos(text: str, pos: str):
    """Refer to https://spacy.io/usage/linguistic-features"""
    ...
