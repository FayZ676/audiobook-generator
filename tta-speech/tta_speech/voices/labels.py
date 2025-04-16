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
        "Simon Vance",
        "old",
        "male",
        f"{Path(__file__).parent}/audios/simon_vance.mp3",
        "It was a traditional cape house, but on a larger scale than usual. A bold architect's airy enlargement.",
    ),
]
