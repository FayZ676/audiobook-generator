from abc import ABC

from tta_types.types import Voice, SpeechRequestSegment


class SpeechGeneratorInterface(ABC):
    def __init__(self, voice: set[Voice]) -> None: ...

    # TODO: Specify return type. It should always be the same.
    def generate(self, segments: list[SpeechRequestSegment]) -> list[str]:
        """Generate speech for each segment, returning the paths of the processed segments."""
        ...
