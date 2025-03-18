from pathlib import Path

from tta.character.extract import get_pronouns, get_speaker_names


def get_text(name: str):
    with open(Path.cwd() / f"../text/{name}", encoding="utf-8") as f:
        return f.read()


def test_get_pronouns():
    
    text = get_text("harrypotter-1.txt")

    character_names = get_speaker_names(text)
    print(f"Extracted Character Names: {character_names}")

    # Expected
    expected_pronouns = {
        "Mr. Dursley": "he/him",
        "Mrs. Dursley": "she/her",
        "Dudley": "he/him",
        "Professor McGonagall": "she/her",
        "Albus Dumbledore": "he/him",
        "Hagrid": "he/him",
    }

    result_pronouns = get_pronouns(text, list(character_names))
    print("Extracted Pronouns:")
    for name, pronoun in result_pronouns.items(): 
        print(f"  {name}: {pronoun}")

    assert result_pronouns == expected_pronouns, f"Expected {expected_pronouns}, but got {result_pronouns}"


if __name__ == "__main__":
    try:
        test_get_pronouns()
        print("Test passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
