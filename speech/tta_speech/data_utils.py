import os
import json
from io import BytesIO
from typing import Optional

from pydantic import BaseModel

from tta_aws.s3 import S3Client

from tta_speech.audio_utils import concat_audio_from_files


s3 = S3Client()


class ManifestSegment(BaseModel):
    id: str
    index: int
    key: str


class AudioManifest(BaseModel):
    narration: dict[str, str]
    segments: list[ManifestSegment]


# TODO: Create TTADataManagerClient class? Should it be its own package?


def load_existing_manifest(
    manifest_key: str, bucket_name: str
) -> Optional[AudioManifest]:
    """Load and validate existing manifest file from S3."""
    manifest_exists = bool(s3.list_files(bucket_name, manifest_key))
    if not manifest_exists:
        return None

    manifest_data = json.loads(s3.get_file(bucket_name, manifest_key).decode("utf-8"))
    return AudioManifest.model_validate(manifest_data)


def create_manifest(
    user_id: str, chapter_name: str, segment_ids: list[str], narration_key: str
) -> AudioManifest:
    """Create a new manifest with the given segment IDs."""
    manifest_segments = [
        ManifestSegment(
            id=seg_id,
            index=idx,
            key=f"{user_id}/{chapter_name}/audio/segments/{seg_id}.mp3",
        )
        for idx, seg_id in enumerate(segment_ids)
    ]

    return AudioManifest(
        narration={"key": narration_key},
        segments=manifest_segments,
    )


def save_manifest_and_narration(
    manifest: AudioManifest,
    manifest_key: str,
    narration_key: str,
    audio_results: dict[str, str],  # TODO: Be more specific about the str types
    bucket_name: str,
) -> None:
    """Save manifest and create stitched narration from audio segments."""
    segment_ids = [s.id for s in manifest.segments]
    ordered_file_paths = [audio_results[seg_id] for seg_id in segment_ids]
    stitched = concat_audio_from_files(ordered_file_paths, audio_format="wav")

    s3.upload_fileobj(bucket_name, narration_key, BytesIO(stitched))
    s3.upload_fileobj(
        bucket_name,
        manifest_key,
        BytesIO(manifest.model_dump_json().encode("utf-8")),
    )


def download_audio(
    audio_path: str, voice_name: str, voices_bucket: str, save_path: str
):
    """Download audio file for voice if it itsn't already downloaded."""
    temp_audio_path = f"{save_path}/{voice_name}.wav"
    if not os.path.exists(temp_audio_path):
        audio = S3Client().get_file(voices_bucket, audio_path)
        with open(temp_audio_path, "wb") as f:
            f.write(audio)
    return temp_audio_path
