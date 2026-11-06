from types import SimpleNamespace

from tta_types.cast import NARRATOR_ID, Cast, CastMember
from tta_script.dialogue import decide as decide_module
from tta_script.dialogue.extract import label_script
from tta_script.dialogue.types import TextSegment
from tta_script.models import decisions
from tta_script.models.decisions import Answer, Choice, Question


CAST = Cast(
    members=[
        CastMember(id="c1", names=["Bob", "Robert"], age="middle-aged", gender="male", voice="b"),
        CastMember(id=NARRATOR_ID, names=["Narrator"], age="middle-aged", gender="male", voice="n"),
    ]
)
SEGMENTS = [
    TextSegment("Hello,", True, 0),
    TextSegment("said Bob.", False, 0),
    TextSegment("Bye.", True, 1),
]


def fake_decide(monkeypatch, answers: dict[str, Answer]):
    calls = []

    def decide(model, evidence, questions):
        calls.append((model, evidence, questions))
        return {q.name: answers[q.name] for q in questions}

    monkeypatch.setattr(decide_module, "decide", decide)
    return calls


def test_decisions_labeller_asks_one_question_per_dialogue_segment(monkeypatch):
    monkeypatch.setenv("TTA_LABEL_MODEL", "openai-decisions:gpt-6-luna")
    calls = fake_decide(
        monkeypatch,
        {"s0": Answer("c1", 0.97), "s2": Answer(NARRATOR_ID, 0.41)},
    )

    script = label_script(SEGMENTS, CAST)

    model, evidence, questions = calls[0]
    assert model == "gpt-6-luna"
    assert [q.name for q in questions] == ["s0", "s2"]
    assert questions[0].instructions == 'Who speaks segment 0 of the chapter: "Hello,"?'
    assert [c.value for c in questions[0].choices] == [NARRATOR_ID, "c1"]
    assert questions[0].choices[1].description == "Bob, Robert"
    assert "0. (D) Hello,\n1. (N) said Bob.\n\n2. (D) Bye." in evidence
    assert [(s.speaker_id, s.confidence) for s in script.segments] == [
        ("c1", 0.97),
        (NARRATOR_ID, None),
        (NARRATOR_ID, 0.41),
    ]


def test_refused_question_goes_to_the_narrator(monkeypatch):
    monkeypatch.setenv("TTA_LABEL_MODEL", "openai-decisions:gpt-6-luna")
    fake_decide(monkeypatch, {"s0": Answer(None, 0.0), "s2": Answer("c1", 0.9)})

    script = label_script(SEGMENTS, CAST)

    assert script.segments[0].speaker_id == NARRATOR_ID
    assert script.segments[0].confidence == 0.0


def test_decide_splits_questions_into_requests_of_at_most_400(monkeypatch):
    requests = []

    def create(model, input, questions):  # pylint: disable=redefined-builtin
        requests.append(len(questions))
        answers = [
            SimpleNamespace(type="choice", name=q["name"], choice="a", confidence=0.5) for q in questions
        ]
        details = SimpleNamespace(cached_tokens=0)
        usage = SimpleNamespace(input_tokens=10, input_tokens_details=details, output_tokens=0)
        return SimpleNamespace(answers=answers, usage=usage)

    client = SimpleNamespace(decisions=SimpleNamespace(create=create))
    monkeypatch.setattr(decisions, "_client", lambda: client)
    choices = (Choice("a", "A"), Choice("b", "B"))
    questions = [Question(f"q{i}", "?", choices) for i in range(401)]

    answers = decisions.decide("gpt-6-luna", "evidence", questions)

    assert requests == [400, 1]
    assert len(answers) == 401
    assert answers["q400"] == Answer("a", 0.5)
