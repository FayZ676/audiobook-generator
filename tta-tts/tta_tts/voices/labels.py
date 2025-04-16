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
        "Standing on a golden perch behind the door was a decrepit looking bird that resembled a half plucked turkey. Harry stared at it and the bird looked balefully back, making it's gagging noise again.",
    ),
    Voice(
        "Elizabeth Gaskell",
        "middle-aged",
        "female",
        f"{Path(__file__).parent}/audios/elizabeth_gaskell.mp3",
        "Still there was a neat little quilling inside, every plat of which Molly knew. For had she not made it herself the evening before, with infinite pains? And was there not a little blue bow in this quilling, the very first bit of such finery Molly had ever had the prospect of wearing?",
    ),
    Voice(
        "Michael Gambon",
        "old",
        "male",
        f"{Path(__file__).parent}/audios/michael_gambon.mp3",
        "I will never speak to you again and I said okay I'll do it, I'll do it. She's wrapped up in it, you know and I love the book, I love the script. I'ts beautifully written, beautiful dialogue in it.",
    ),
]
