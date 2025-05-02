import spacy
from spacy.language import Language
from spacy.tokens import Span, Doc

from tta_script.text_utils import HONORIFICS


def is_plural(ent: Span):
    if any(token.morph.get("Number", []) == ["Plur"] for token in ent):
        return True
    return False


# NOTE: Refer to https://spacy.io/usage/processing-pipelines#custom-components.
@Language.component("custom_person")
def custom_person(doc: Doc):
    new_ents = []
    for ent in doc.ents:
        if ent.label_ != "PERSON":
            new_ents.append(ent)
            continue
        if is_plural(ent):
            continue
        if ent.start > 0 and doc[ent.start - 1].text in HONORIFICS:
            new_ents.append(Span(doc, ent.start - 1, ent.end, label=ent.label))
        else:
            new_ents.append(ent)
    doc.ents = new_ents
    return doc


class NER:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_trf")
        self.nlp.add_pipe("custom_person", after="ner")

    def find_names(self, text: str):
        doc = self.nlp(text)
        names = {ent.text for ent in doc.ents if ent.label_ == "PERSON"}
        return names

    def is_pos(self, text: str, pos: str) -> bool:
        doc = self.nlp(text)
        for token in doc:
            if token.pos_ == pos:
                return True
        return False
