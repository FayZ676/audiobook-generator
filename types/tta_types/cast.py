"""The cast of a book: every character, the names they go by, and their voice.

Characters are identified by id, never by name. Names are aliases: a
character gains names as the book goes on ("Mr. Dursley", later "Uncle
Vernon"), and one name can belong to several characters ("Professor").
"""

from pydantic import BaseModel, Field

from tta_types.types import Age, Gender


NARRATOR_ID = "narrator"


class CastMember(BaseModel):
    id: str
    names: list[str]  # The first name is the one shown to people.
    age: Age
    gender: Gender
    voice: str  # Voice.name

    @property
    def name(self) -> str:
        return self.names[0]


class Cast(BaseModel):
    members: list[CastMember] = Field(default_factory=list)

    def get(self, member_id: str) -> CastMember | None:
        return next((m for m in self.members if m.id == member_id), None)

    def next_id(self) -> str:
        """A new character id: c1, c2, ... never reusing a number."""
        numbers = [int(m.id[1:]) for m in self.members if m.id[:1] == "c" and m.id[1:].isdigit()]
        return f"c{max(numbers, default=0) + 1}"
