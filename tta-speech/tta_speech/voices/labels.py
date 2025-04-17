from pathlib import Path

from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Voice:
    name: str
    age: str
    gender: str
    audio_path: str
    audio_transcript: str


voices = [
    Voice(
        "Jim Dale",
        "middle-aged",
        "male",
        f"{Path(__file__).parent}/audios/jim_dale.mp3",
        "Mr. Vernon Dursley had been woken in the early hours of the morning by a loud hooting noise from his nephew Harry's room.",
    ),
    Voice(
        "Elizabeth Gaskell",
        "middle-aged",
        "female",
        f"{Path(__file__).parent}/audios/elizabeth_gaskell.mp3",
        "When she wakened of herself, as sure as clockwork, and left the household very little peace afterwards.",
    ),
    Voice(
        "Arthur Lane",
        "middle-aged",
        "male",
        f"{Path(__file__).parent}/audios/arthur_lane.mp3",
        "Carter Wetherby threw up his snug clarkship, turned the half of his savings over to his wife, and with the remainder bought an outfit.",
    ),
    Voice(
        "Stephen Fry",
        "old",
        "male",
        f"{Path(__file__).parent}/audios/stephen_fry.mp3",
        "At the moment, cosmos is chaos and only chaos because chaos is the only thing that is the case.",
    ),
]
