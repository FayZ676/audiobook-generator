import spacy
from spacy.language import Language
from spacy.tokens import Span, Doc

from tta.text_utils import HONORIFICS
from tta.character.types import SpeakerDetails


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

    def find_speaker(
        self, preceeding_text: str, following_text: str, names: set[str]
    ) -> str | None:
        def analyze_following(text: str):
            doc_following = self.nlp(text.strip())
            if len(doc_following) > 1 and doc_following[0].pos_ == "VERB":
                for ent in doc_following.ents:
                    if ent.label_ == "PERSON" and ent.start == 1 and ent.text in names:
                        return ent.text
                if doc_following[1].text in names:
                    return doc_following[1].text

        def analyze_preceeding(text: str):
            doc_preceeding = self.nlp(text.strip())
            if len(doc_preceeding) > 1:
                last_verb_token = None
                for i in range(len(doc_preceeding) - 1, -1, -1):
                    token = doc_preceeding[i]
                    if token.pos_ == "PUNCT":
                        continue
                    if token.pos_ == "VERB":
                        last_verb_token = token
                    break
                if last_verb_token:
                    for ent in doc_preceeding.ents:
                        if (
                            ent.label_ == "PERSON"
                            and ent.end == last_verb_token.i
                            and ent.text in names
                        ):
                            return ent.text
                    if (
                        last_verb_token.i > 0
                        and doc_preceeding[last_verb_token.i - 1].text in names
                    ):
                        return doc_preceeding[last_verb_token.i - 1].text

        if preceeding := analyze_preceeding(preceeding_text):
            return preceeding
        elif following := analyze_following(following_text):
            return following
        return None
