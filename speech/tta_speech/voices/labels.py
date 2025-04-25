from pathlib import Path

from tta_speech.types import Voice


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
    Voice(
        "Richard Armitage",
        "middle-aged",
        "male",
        f"{Path(__file__).parent}/audios/richard_armitage.mp3",
        "The first of our three golden rules; One, send a message to let us know where you are, closely followed by two, stick to your curfew.",
    ),
    Voice(
        "Cathleen McCarron",
        "middle-aged",
        "female",
        f"{Path(__file__).parent}/audios/cathleen_mccarron.mp3",
        "Bessy Brunson took a deep breath and prepared to climb a flight of stairs for what seemed like the hundredth time since sunrise. It was not yet noon.",
    ),
]
