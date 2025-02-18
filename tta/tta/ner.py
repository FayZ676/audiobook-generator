from dataclasses import dataclass

import spacy


nlp = spacy.load("en_core_web_trf")


@dataclass(eq=True, frozen=True)
class EntityInfo:
    text: str
    start: int
    end: int
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
                    label=ent.label_,
                )
            )
    return result


# TODO: Implement
def is_pos(text: str, pos: str) -> bool:
    """
    Refer to https://spacy.io/usage/linguistic-features
    This takes some text and a part of speech (i.e. verb, adjective, etc.) and returns whether the word is that part of speech or not using spacy's part of speech tagger.
    """
    ...
