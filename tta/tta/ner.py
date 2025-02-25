from dataclasses import dataclass

import spacy
from spacy.language import Language
from spacy.tokens import Span


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


@Language.component("expand_persons")
def expand_persons(doc):
    new_ents = []
    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.start != 0:
            prev_token = doc[ent.start - 1]
            if prev_token.text in HONORIFICS:
                new_ent = Span(doc, ent.start - 1, ent.end, label=ent.label)
                new_ents.append(new_ent)
            else:
                new_ents.append(ent)
        else:
            new_ents.append(ent)
    doc.ents = new_ents
    return doc


class NER:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_trf")
        self.nlp.add_pipe("expand_persons", after="ner")

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
