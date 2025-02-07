import re
import spacy
import requests
from collections import Counter

# Loading SpaCy
nlp = spacy.load("en_core_web_trf")

def read_from_file(file_path):
    """ Reads text from a local file. """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def remove_quoted_text(paragraph):
    """ Removes text inside quotation marks. """
    return re.sub(r'["\'].*?["\']', '', paragraph)

def extract_speakers(text):
    """
    Extracts and counts the frequency of named entities from paragraphs containing quotes.
    """
    # Splitting text into paragraphs
    paragraphs = text.split("\n\n")  

    # Filerting only paragraphs with quotation marks
    quoted_paragraphs = [p for p in paragraphs if '"' in p or "'" in p]

    # Remove text inside quotes
    filtered_paragraphs = [remove_quoted_text(p) for p in quoted_paragraphs]

    # Apply NER to extract names
    speaker_counts = Counter()
    
    for paragraph in filtered_paragraphs:
        doc = nlp(paragraph)
        for ent in doc.ents:
            if ent.label_ == "PERSON":  # To extract person names
                speaker_counts[ent.text] += 1

    # Returning a sorted list of speakers from highest to lowest
    return sorted(speaker_counts.items(), key=lambda x: x[1], reverse=True)
