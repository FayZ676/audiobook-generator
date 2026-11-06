import json

from tta_script.dialogue import unmarked
from tta_script.dialogue.unmarked import mark_spoken_lines


def fake_model(monkeypatch, paragraphs: list[dict]):
    prompts: list[str] = []

    def generate_text(_system, prompt, _response_format):
        prompts.append(prompt)
        return json.dumps({"paragraphs": paragraphs})

    monkeypatch.setattr(unmarked, "generate_text", generate_text)
    return prompts


TEXT = "Where you headed? he said.\n\nNowhere, the boy said. Just\nwalking.\n\nThey went on."


def test_the_models_spoken_words_are_put_in_quotes(monkeypatch):
    prompts = fake_model(
        monkeypatch,
        [
            {"paragraph": 0, "spoken": ["Where you headed?"]},
            {"paragraph": 1, "spoken": ["Nowhere,", "Just walking."]},
        ],
    )

    marked = mark_spoken_lines(TEXT)

    assert marked == (
        "“Where you headed?” he said.\n\n"
        "“Nowhere,” the boy said. “Just walking.”\n\n"
        "They went on."
    )
    assert "1. Nowhere, the boy said. Just walking." in prompts[0]


def test_words_the_paragraph_doesnt_contain_are_skipped(monkeypatch):
    fake_model(monkeypatch, [{"paragraph": 0, "spoken": ["Where are you going?"]}, {"paragraph": 9, "spoken": ["x"]}])

    assert mark_spoken_lines(TEXT) == "Where you headed? he said.\n\nNowhere, the boy said. Just walking.\n\nThey went on."


def test_text_that_marks_its_speech_is_left_alone(monkeypatch):
    prompts = fake_model(monkeypatch, [])
    text = '"Hi," he said.\n\n"Bye," she said.'

    assert mark_spoken_lines(text) == text
    assert not prompts
