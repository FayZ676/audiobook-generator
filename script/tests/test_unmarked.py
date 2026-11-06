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
    text = '\n\n'.join(f'"Line {i}," he said.' for i in range(5))

    assert mark_spoken_lines(text) == text
    assert not prompts


def test_a_few_quoted_lines_dont_stop_the_model_finding_the_rest(monkeypatch):
    text = (
        "The sign said \u201cNo Trespassing\u201d in red.\n\n"
        "Where you headed? he said.\n\n"
        "\u201cNowhere,\u201d the boy said. Just walking.\n\n"
        "You hungry? the man said.\n\n"
        "Some, said the boy."
    )
    prompts = fake_model(
        monkeypatch,
        [
            {"paragraph": 1, "spoken": ["Where you headed?"]},
            {"paragraph": 2, "spoken": ["Nowhere,", "Just walking."]},
            {"paragraph": 3, "spoken": ["You hungry?"]},
            {"paragraph": 4, "spoken": ["Some,"]},
        ],
    )

    marked = mark_spoken_lines(text)

    assert prompts
    assert marked.split("\n\n") == [
        "The sign said \u201cNo Trespassing\u201d in red.",
        "\u201cWhere you headed?\u201d he said.",
        "\u201cNowhere,\u201d the boy said. \u201cJust walking.\u201d",
        "\u201cYou hungry?\u201d the man said.",
        "\u201cSome,\u201d said the boy.",
    ]


def test_indirect_speech_in_a_quoted_book_doesnt_call_the_model(monkeypatch):
    prompts = fake_model(monkeypatch, [])
    text = "\n\n".join(
        [f"“Line {i},” said Bob." for i in range(3)] + ["Scrooge said that he would see him first."]
    )

    assert mark_spoken_lines(text) == text
    assert not prompts
