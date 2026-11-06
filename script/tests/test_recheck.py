import json

from tta_script.cast import NARRATOR_ID, Cast, CastMember
from tta_script.dialogue import recheck
from tta_script.dialogue.recheck import recheck_lines
from tta_script.script import Script, ScriptSegment

CAST = Cast(
    members=[
        CastMember(id=NARRATOR_ID, names=["Narrator"], age="middle-aged", gender="male"),
        CastMember(id="c1", names=["Bob"], age="middle-aged", gender="male"),
        CastMember(id="c2", names=["Mary"], age="young", gender="female"),
    ]
)


def line(i, text, speaker, confidence=None, dialogue=True):
    return ScriptSegment(
        id=f"seg-{i}", text=text, speaker_id=speaker, is_dialogue=dialogue, paragraph=i, confidence=confidence
    )


SCRIPT = Script(
    segments=[
        line(0, "Bob came in.", NARRATOR_ID, dialogue=False),
        line(1, "Hello", "c1", 0.99),
        line(2, "Hi", "c1", 0.40),
        line(3, "How are you?", "c1", 0.95),
        line(4, "Fine", "c2", 0.97),
        line(5, "Good", "c2", 0.30),
    ]
)


def fake_model(monkeypatch, answers):
    prompts = []

    def generate_text(_system, prompt, _response_format, **kwargs):
        prompts.append((prompt, kwargs))
        return json.dumps({"dialogue": [{"index": i, "speaker": s} for i, s in answers.items()]})

    monkeypatch.setattr(recheck, "generate_text", generate_text)
    return prompts


def test_lines_asked_about_are_answered_in_one_request(monkeypatch):
    prompts = fake_model(monkeypatch, {2: "c2", 5: "c1"})

    answers = recheck_lines(SCRIPT, CAST, [5, 2])

    assert len(prompts) == 1
    prompt, kwargs = prompts[0]
    assert kwargs["model_name"] == recheck.RECHECK_MODEL
    asked = prompt.split("## Your task")[1]
    assert '2. "Hi"' in asked and '5. "Good"' in asked and "Hello" not in asked
    assert answers == {2: "c2", 5: "c1"}


def test_the_first_labels_are_not_shown(monkeypatch):
    prompts = fake_model(monkeypatch, {})

    recheck_lines(SCRIPT, CAST, [2])

    assert "->" not in prompts[0][0] and "Bob" in prompts[0][0]


def test_answers_for_lines_not_asked_are_ignored(monkeypatch):
    fake_model(monkeypatch, {1: "c2", 5: "c2"})

    assert recheck_lines(SCRIPT, CAST, [5]) == {5: "c2"}


def test_cached_requests_send_the_chapter_as_the_cached_prefix(monkeypatch):
    prompts = fake_model(monkeypatch, {})

    recheck_lines(SCRIPT, CAST, [2], cache=True)

    prompt, kwargs = prompts[0]
    assert "Bob came in." in kwargs["cached_prefix"] and "Bob came in." not in prompt
    assert '2. "Hi"' in prompt


def test_nothing_asked_makes_no_request(monkeypatch):
    prompts = fake_model(monkeypatch, {})

    assert not recheck_lines(SCRIPT, CAST, [])
    assert not prompts
