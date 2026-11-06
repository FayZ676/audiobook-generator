import json

from tta_script.cast import NARRATOR_ID, Cast, CastMember
from tta_script.dialogue import recheck
from tta_script.dialogue.recheck import recheck_script
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


def test_only_the_least_confident_lines_are_asked_in_one_request(monkeypatch):
    prompts = fake_model(monkeypatch, {2: "c2", 5: "c1"})

    result = recheck_script(SCRIPT, CAST, share=0.4)

    assert len(prompts) == 1
    prompt, kwargs = prompts[0]
    assert kwargs["model_name"] == recheck.RECHECK_MODEL
    asked = prompt.split("## Your task")[1]
    assert '2. "Hi"' in asked and '5. "Good"' in asked and "Hello" not in asked
    assert [s.recheck_speaker_id for s in result.segments] == [None, None, "c2", None, None, "c1"]
    assert [s.speaker_id for s in result.segments] == [s.speaker_id for s in SCRIPT.segments]


def test_the_first_labels_are_not_shown(monkeypatch):
    prompts = fake_model(monkeypatch, {})

    recheck_script(SCRIPT, CAST, share=0.4)

    assert "->" not in prompts[0][0] and "Bob" in prompts[0][0]


def test_answers_for_lines_not_asked_are_ignored(monkeypatch):
    fake_model(monkeypatch, {1: "c2", 2: "c2"})

    result = recheck_script(SCRIPT, CAST, share=0.2)

    assert result.segments[1].recheck_speaker_id is None


def test_nothing_to_recheck_makes_no_request(monkeypatch):
    prompts = fake_model(monkeypatch, {})

    recheck_script(Script(segments=[line(0, "Quiet.", NARRATOR_ID, dialogue=False)]), CAST)

    assert not prompts
