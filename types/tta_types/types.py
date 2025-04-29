from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class Voice:
    name: str
    age: str
    gender: str
    audio_path: str
    audio_transcript: str

    def audio_to_dict(self) -> dict[str, str]:
        return {
            "ref_audio": self.audio_path,
            "ref_text": self.audio_transcript,
        }
