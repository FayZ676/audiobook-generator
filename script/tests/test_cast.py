from tta_script.cast import NARRATOR_ID, Cast, CastMember


def member(member_id: str, voice: str = "v") -> CastMember:
    return CastMember(id=member_id, names=[member_id], age="young", gender="male", voice=voice)


def test_next_id_starts_at_c1_and_skips_non_numbered_ids():
    assert Cast().next_id() == "c1"
    assert Cast(members=[member(NARRATOR_ID), member("c2"), member("c10")]).next_id() == "c11"
