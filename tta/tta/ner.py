from dataclasses import dataclass

import spacy


# TODO: Use en_core_web_trf instead
nlp = spacy.load("en_core_web_sm")


@dataclass(eq=True, frozen=True)
class EntityInfo:
    text: str
    start: int
    end: int
    pos: str
    label: str


def extract_entities(text: str, entities: list[str]) -> list[EntityInfo]:
    doc = nlp(text)
    result: list[EntityInfo] = []
    for ent in doc.ents:
        if ent.label_ in entities:
            result.append(
                EntityInfo(
                    text=ent.text,
                    start=ent.start_char,
                    end=ent.end_char,
                    pos=ent.root.pos_,
                    label=ent.label_,
                )
            )
    return result


# TODO: Implement
def extract_pos(text: str, pos: str):
    """Refer to https://spacy.io/usage/linguistic-features"""
    ...
