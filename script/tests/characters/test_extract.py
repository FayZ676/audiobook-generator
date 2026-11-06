import json

import pytest

from tta_script.cast import NARRATOR_ID, Cast, CastMember, Voice
from tta_script.character import extract
from tta_script.character.extract import update_cast


def voice(name, age="middle-aged", gender="male"):
    return Voice(name=name, age=age, gender=gender, audio_path="", audio_transcript="")


VOICES = [
    voice("narrator-voice"),
    voice("man"),
    voice("woman", gender="female"),
    voice("boy", age="young"),
]


def fake_model(monkeypatch, *replies: dict):
    """Make the model return each reply in turn; record the prompts it got."""
    prompts: list[str] = []
    replies_iter = iter(replies)

    def generate_text(_system, prompt, _response_format):
        prompts.append(prompt)
        reply = next(replies_iter)
        return json.dumps(
            {
                "known": reply.get("known", []),
                "new": reply.get("new", []),
                "narrator_names": reply.get("narrator_names", []),
            }
        )

    monkeypatch.setattr(extract, "generate_text", generate_text)
    return prompts


def new(*names, age="middle-aged", gender="male"):
    return {"names": list(names), "age": age, "gender": gender}


def member(member_id, *names, age="middle-aged", gender="male", voice_name="man"):
    return CastMember(id=member_id, names=list(names), age=age, gender=gender, voice=voice_name)


def first_chapter_cast():
    return Cast(
        members=[
            member(NARRATOR_ID, "Narrator", voice_name="narrator-voice"),
            member("c1", "Mr. Dursley"),
        ]
    )


def test_first_chapter_adds_narrator_and_numbers_new_characters(monkeypatch):
    fake_model(monkeypatch, {"new": [new("Mr. Dursley"), new("Mrs. Dursley", gender="female")]})

    cast = update_cast("text", Cast(), VOICES)

    assert cast.members == [
        member(NARRATOR_ID, "Narrator", voice_name="narrator-voice"),
        member("c1", "Mr. Dursley", voice_name="man"),
        member("c2", "Mrs. Dursley", gender="female", voice_name="woman"),
    ]


def test_known_character_gains_new_names_and_keeps_id_and_voice(monkeypatch):
    prompts = fake_model(
        monkeypatch, {"known": [{"id": "c1", "new_names": ["Uncle Vernon", "mr. dursley"]}]}
    )

    cast = update_cast("text", first_chapter_cast(), VOICES)

    assert cast.get("c1") == member("c1", "Mr. Dursley", "Uncle Vernon")
    assert len(cast.members) == 2
    assert "- c1: Mr. Dursley" in prompts[0]
    assert "Narrator" not in prompts[0].split("<known_characters>")[1]


def test_update_does_not_change_the_cast_passed_in(monkeypatch):
    fake_model(monkeypatch, {"known": [{"id": "c1", "new_names": ["Uncle Vernon"]}]})
    original = first_chapter_cast()

    update_cast("text", original, VOICES)

    assert original == first_chapter_cast()


def test_unknown_or_narrator_ids_are_ignored(monkeypatch):
    fake_model(
        monkeypatch,
        {"known": [{"id": "c99", "new_names": ["Ghost"]}, {"id": NARRATOR_ID, "new_names": ["Me"]}]},
    )

    cast = update_cast("text", first_chapter_cast(), VOICES)

    assert cast == first_chapter_cast()


def test_new_character_matching_one_known_name_is_merged_into_it(monkeypatch):
    fake_model(monkeypatch, {"new": [new("Vernon Dursley", "Mr. Dursley")]})

    cast = update_cast("text", first_chapter_cast(), VOICES)

    assert [m.id for m in cast.members] == [NARRATOR_ID, "c1"]
    assert cast.get("c1").names == ["Mr. Dursley", "Vernon Dursley"]


def test_name_shared_by_several_known_characters_makes_a_new_character(monkeypatch):
    cast = Cast(
        members=[
            member(NARRATOR_ID, "Narrator"),
            member("c1", "Fred Weasley", "Weasley"),
            member("c2", "George Weasley", "Weasley"),
        ]
    )
    fake_model(monkeypatch, {"new": [new("Ron Weasley", "Weasley", age="young")]})

    cast = update_cast("text", cast, VOICES)

    assert cast.get("c3").names == ["Ron Weasley", "Weasley"]


def test_narrator_and_blank_names_are_never_added(monkeypatch):
    fake_model(monkeypatch, {"new": [new("Narrator"), new(" ", ""), new(" Hagrid ", "Hagrid", "")]})

    cast = update_cast("text", first_chapter_cast(), VOICES)

    assert [m.names for m in cast.members[2:]] == [["Hagrid"]]


def test_ids_keep_counting_after_the_highest_existing_one(monkeypatch):
    cast = Cast(members=[member(NARRATOR_ID, "Narrator"), member("c4", "Hagrid")])
    fake_model(monkeypatch, {"new": [new("Dudley", age="young")]})

    assert update_cast("text", cast, VOICES).members[-1].id == "c5"


def test_long_text_is_split_and_later_chunks_see_earlier_finds(monkeypatch):
    monkeypatch.setattr(extract, "CHUNK_WORDS", 3)
    prompts = fake_model(monkeypatch, {"new": [new("Hagrid")]}, {"known": [], "new": []})

    update_cast("one two three\n\nfour five six", Cast(), VOICES)

    assert len(prompts) == 2
    assert "- c1: Hagrid" in prompts[1]


def test_no_voices_is_an_error():
    with pytest.raises(ValueError, match="No voices"):
        update_cast("text", Cast(), [])


def test_invalid_reply_raises(monkeypatch):
    fake_model(monkeypatch, {"new": [new("Hagrid", age="ancient")]})

    with pytest.raises(ValueError):
        update_cast("text", Cast(), VOICES)


def test_a_first_person_narrator_joins_the_narrator_instead_of_the_cast(monkeypatch):
    prompts = fake_model(
        monkeypatch,
        {"narrator_names": ["Dr. Watson", "Watson"], "new": [new("Watson"), new("Sherlock Holmes")]},
        {"known": [{"id": NARRATOR_ID, "new_names": ["John"]}]},
    )

    cast = update_cast("text", Cast(), VOICES)
    cast = update_cast("more text", cast, VOICES)

    assert cast.get(NARRATOR_ID).names == ["Narrator", "Dr. Watson", "Watson", "John"]
    assert [m.names for m in cast.members if m.id != NARRATOR_ID] == [["Sherlock Holmes"]]
    assert "- narrator: Narrator, Dr. Watson, Watson" in prompts[1]
