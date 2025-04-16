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
        "Faizi",
        "young",
        "male",
        f"{Path(__file__).parent}/audios/faizi.mp3",
        "The little red fox jumped over the white picket fence and onto the crocodile that was sitting on the roof of the house. He didn't realize that there was a flamingo sitting up there with him.",
    ),
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
        "Michael Gambon",
        "old",
        "male",
        f"{Path(__file__).parent}/audios/michael_gambon.mp3",
        "I will never speak to you again and I said okay I'll do it, I'll do it. She's wrapped up in it, you know and I love the book, I love the script. I'ts beautifully written, beautiful dialogue in it.",
    ),
]
