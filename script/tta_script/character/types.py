from typing import Literal

from pydantic import BaseModel


Age = Literal["young", "middle-aged", "old"]
Gender = Literal["male", "female"]


class FoundCharacter(BaseModel):
    names: list[str]
    age: Age
    gender: Gender


class CharactersResponse(BaseModel):
    characters: list[FoundCharacter]
