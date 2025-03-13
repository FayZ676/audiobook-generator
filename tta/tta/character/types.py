from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel


type Age = Literal["young", "middle-aged", "old"]
type Gender = Literal["male", "female"]


@dataclass(eq=True, frozen=True)
class Character:
    name: str
    age: Age
    gender: Gender


@dataclass(eq=True, frozen=True)
class SpeakerDetails:
    names: frozenset[str]
    age: Age
    gender: Gender


class SpeakersResponse(BaseModel):
    response: list[Character]


class AliasResponse(BaseModel):
    aliases: list[list[str]]


class AgesResponse(BaseModel):
    ages: list[str]


class GendersResponse(BaseModel):
    genders: list[str]
