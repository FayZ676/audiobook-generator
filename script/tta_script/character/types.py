from typing import Literal

from pydantic import BaseModel


Age = Literal["young", "middle-aged", "old"]
Gender = Literal["male", "female"]


class AliasResponse(BaseModel):
    aliases: list[list[str]]


class AgesResponse(BaseModel):
    ages: list[str]


class GendersResponse(BaseModel):
    genders: list[str]
