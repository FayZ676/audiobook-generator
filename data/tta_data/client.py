import io
import os
import json
from io import BytesIO
from typing import BinaryIO

from tta_types.types import Script, AudioManifest, ManifestSegment

from tta_data.s3 import S3Client


class TTADataClient:
    def __init__(self):
        self.s3_client = S3Client()
        # TODO: Pass in bucket name
        self.voices_bucket = os.environ.get("VOICES_BUCKET", "")
        self.projects_bucket = os.environ.get("PROJECTS_BUCKET", "")

    ### Scripts ###

    def get_script(self, user_id: str, chapter_name: str): ...

    def upload_script(self, user_id: str, script: Script, chapter_name: str):
        script_file = script_to_json_fileobject("script.json", script)
        project_script_path = f"{user_id}/{chapter_name}/script.json"
        self.s3_client.upload_fileobj(
            f"{self.projects_bucket}", project_script_path, script_file
        )
        return str(script_file.name)

    def delete_script(self): ...

    ### Voices ###

    def get_voice(self, voice_audio_file_path: str, voice_name: str, save_path: str):
        temp_audio_path = f"{save_path}/{voice_name}.wav"
        if not os.path.exists(temp_audio_path):
            audio = self.s3_client.get_file(self.voices_bucket, voice_audio_file_path)
            with open(temp_audio_path, "wb") as f:
                f.write(audio)
        return temp_audio_path

    ### Speech ###

    def get_speech_manifest(self, user_id: str, chapter_name: str):
        manifest_key = f"{user_id}/{chapter_name}/audio/manifest.json"
        manifest_exists = bool(
            self.s3_client.list_files(self.projects_bucket, manifest_key)
        )
        if not manifest_exists:
            return None

        manifest_data = json.loads(
            self.s3_client.get_file(self.projects_bucket, manifest_key).decode("utf-8")
        )
        return AudioManifest.model_validate(manifest_data)

    def upload_speech_manifest(
        self, user_id: str, chapter_name: str, segment_ids: list[str]
    ):
        manifest = create_manifest(
            user_id=user_id,
            chapter_name=chapter_name,
            segment_ids=segment_ids,
            narration_key=f"{user_id}/{chapter_name}/audio/narration.mp3",
        )
        self.s3_client.upload_fileobj(
            bucket_name=self.projects_bucket,
            file_name=f"{user_id}/{chapter_name}/audio/manifest.json",
            file=audio_manifest_to_json_fileobject(
                audio_manifest=manifest, file_name="manifest.json"
            ),
        )

    def upload_speech(self, user_id: str, chapter_name: str, speech_file_path: str):
        narration_key = f"{user_id}/{chapter_name}/audio/narration.mp3"
        self.s3_client.upload_fileobj(
            bucket_name=self.projects_bucket,
            file_name=narration_key,
            file=audio_file_to_bytesio(speech_file_path),
        )
        return narration_key

    ### Job State ###

    ### Project ###

    ### Chapter ###


def create_manifest(
    user_id: str, chapter_name: str, segment_ids: list[str], narration_key: str
) -> AudioManifest:
    """Create a new manifest with the given segment IDs."""
    return AudioManifest(
        narration={"key": narration_key},
        segments=[
            ManifestSegment(
                id=seg_id,
                index=idx,
                key=f"{user_id}/{chapter_name}/audio/segments/{seg_id}.mp3",
            )
            for idx, seg_id in enumerate(segment_ids)
        ],
    )


def script_to_json_fileobject(filename: str, script_data: Script) -> BinaryIO:
    json_data = script_data.model_dump()
    json_bytes = json.dumps(json_data, indent=4).encode("utf-8")
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = f"{filename}"
    return file_obj


def audio_manifest_to_json_fileobject(
    audio_manifest: AudioManifest, file_name: str
) -> BinaryIO:
    """Convert an AudioManifest object to a JSON file object."""
    json_data = audio_manifest.model_dump()
    json_bytes = json.dumps(json_data, indent=4).encode("utf-8")
    file_obj = io.BytesIO(json_bytes)
    file_obj.name = file_name
    return file_obj


def audio_file_to_bytesio(file_path: str) -> BytesIO:
    with open(file_path, "rb") as audio_file:
        audio_data = audio_file.read()
    return BytesIO(audio_data)
