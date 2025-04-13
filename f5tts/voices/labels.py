from pathlib import Path

from dataclasses import dataclass


@dataclass
class Voice:
    name: str
    audio_path: str
    audio_transcript: str


voices = [
    Voice(
        "Faizi",
        f"{Path(__file__).parent}/audios/faizi.mp3",
        "The little red fox jumped over the white picket fence and onto the crocodile that was sitting on the roof of the house. He didn't realize that there was a flamingo sitting up there with him.",
    )
]
