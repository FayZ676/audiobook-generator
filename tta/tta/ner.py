from dataclasses import dataclass

import spacy
from spacy.language import Language
from spacy.tokens import Span, Doc, Token


@dataclass(eq=True, frozen=True)
class EntityInfo:
    text: str
    start_char: int
    end_char: int
    label: str


HONORIFICS = [
    "Dr",
    "Dr.",
    "Mr",
    "Mr.",
    "Ms",
    "Ms.",
    "Mrs.",
    "Uncle",
    "Aunt",
    "Professor",
]


def is_name_part(token: Token):
    if token.text in HONORIFICS or token.pos_ == "PROPN":
        return True


# NOTE: Refer to https://spacy.io/usage/processing-pipelines#custom-components.
@Language.component("custom_person")
def custom_person(doc: Doc):
    new_ents = []
    for ent in doc.ents:
        if ent.label == "PERSON" and ent.start != 0:
            if is_name_part(doc[ent.start - 1]):
                new_ents.append(Span(doc, ent.start - 1, ent.end, label=ent.label))
            else:
                new_ents.append(ent)
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
