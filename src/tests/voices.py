from dataclasses import dataclass
from typing import List

@dataclass
class Voice:
    id: str         # Unique ID for the voice
    name: str       # Name of the voice
    gender: str     # Gender (e.g., male, female, non-binary)
    age_group: str  # Age category (e.g., child, young-adult, middle-aged, elderly)
    traits: List[str]  # List of traits (e.g., "calm", "cheerful")
    url: str        # URL linking to the ElevenLabs voice page

# Predefined catalogue of voices with a variety of traits, 2 per age group
voices_catalogue = [
    # Child voices
    Voice(
        id="voice_id_1",
        name="Beatrice",
        gender="female",
        age_group="child",
        traits=["whimsical", "high-pitched", "cheerful"],
        url="https://beta.elevenlabs.io/voice/wu317loZrCqh7kM2gCcr"
    ),
    Voice(
        id="voice_id_2",
        name="Christopher",
        gender="male",
        age_group="child",
        traits=["bright", "enthusiastic", "fast-talking"],
        url="https://beta.elevenlabs.io/voice/DHeSUVQvhhYeIxNUbtj3"
    ),

    # Young-adult voices
    Voice(
        id="voice_id_3",
        name="Sexy Female Villain Voice",
        gender="female",
        age_group="young-adult",
        traits=["seductive", "villainous", "dramatic"],
        url="https://beta.elevenlabs.io/voice/eVItLK1UvXctxuaRV2Oq"
    ),
    Voice(
        id="voice_id_4",
        name="Astro",
        gender="male",
        age_group="young-adult",
        traits=["charismatic", "smooth", "energetic"],
        url="https://beta.elevenlabs.io/voice/B5vjwBxGgp4GLTiUjDxM"
    ),

    # Middle-aged voices
    Voice(
        id="voice_id_5",
        name="Eve",
        gender="female",
        age_group="middle-aged",
        traits=["calm", "soothing", "narrative"],
        url="https://beta.elevenlabs.io/voice/ZPH1u1uUFhJCEh1yeJXJ"
    ),
    Voice(
        id="voice_id_6",
        name="Lucius Aurelius",
        gender="male",
        age_group="middle-aged",
        traits=["gruff", "tough", "commanding"],
        url="https://beta.elevenlabs.io/voice/iZhLOEhfNvZn57Cidxck"
    ),

    # Elderly voices
    Voice(
        id="voice_id_7",
        name="Bill",
        gender="male",
        age_group="elderly",
        traits=["raspy", "wise", "gruff"],
        url="https://beta.elevenlabs.io/voice/pqHfZKP75CvOlQylNhV4
"
    ),
    Voice(
        id="voice_id_8",
        name="Elizabeth",
        gender="female",
        age_group="elderly",
        traits=["formal", "grand", "authoritative"],
        url="https://beta.elevenlabs.io/voice/2xuhgVKr0whbJVOvhSUS"
    )
]
