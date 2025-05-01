import json
import io
from dataclasses import dataclass, asdict
from typing import BinaryIO


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

    def to_json_fileobject(self) -> BinaryIO:
        json_bytes = json.dumps(asdict(self), indent=4).encode("utf-8")
        file_obj = io.BytesIO(json_bytes)
        file_obj.name = f"{self.name}.json"
        return file_obj
