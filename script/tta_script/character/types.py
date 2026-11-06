from pydantic import BaseModel

from tta_script.cast import Age, Gender


class KnownCharacter(BaseModel):
    id: str
    new_names: list[str]


class NewCharacter(BaseModel):
    names: list[str]
    age: Age
    gender: Gender


class CastUpdate(BaseModel):
    """What the model reports for one chunk of text."""

    known: list[KnownCharacter]
    new: list[NewCharacter]
