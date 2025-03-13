from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel


@dataclass(eq=True, frozen=True)
class Character:
    name: str
    age: Literal["young", "middle-aged", "old"]
    gender: Literal["male", "female"]


@dataclass(eq=True, frozen=True)
class SpeakerDetails:
    names: frozenset[str]
    age: Literal["young", "middle-aged", "old"]
    gender: Literal["male", "female"]


class SpeakersResponse(BaseModel):
    response: list[Character]


class AliasResponse(BaseModel):
    aliases: list[list[str]]


class AgesResponse(BaseModel):
    ages: list[str]


class GendersResponse(BaseModel):
    genders: list[str]
