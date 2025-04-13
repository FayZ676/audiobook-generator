from pathlib import Path

from dataclasses import dataclass


@dataclass
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
        "young",
        f"{Path(__file__).parent}/audios/jim_dale.mp3",
        "Standing on a golden perch behind the door was a decrepit looking bird that resembled a half plucked turkey. Harry stared at it and the bird looked balefully back, making it's gagging noise again."
    )
]
