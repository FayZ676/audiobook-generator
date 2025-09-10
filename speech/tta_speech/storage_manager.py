"""S3 storage operations for speech synthesis artifacts."""

import json
from io import BytesIO
from typing import Optional, List, Dict, Any

from tta_aws.s3 import S3Client


class StorageManager:
    """Manages S3 storage operations for audio files and manifests."""

    def __init__(self, s3_client: S3Client, projects_bucket: str):
        self.s3_client = s3_client
        self.projects_bucket = projects_bucket

    def upload_segment_audio(
        self, user_id: str, chapter_name: str, segment_id: str, audio_data: bytes
    ) -> str:
        """Upload audio segment to S3 and return the key."""
        key = f"{user_id}/{chapter_name}/audio/segments/{segment_id}.mp3"
        self.s3_client.upload_fileobj(self.projects_bucket, key, BytesIO(audio_data))
        return key

    def upload_narration_audio(
        self, user_id: str, chapter_name: str, audio_data: bytes
    ) -> str:
        """Upload complete narration audio to S3 and return the key."""
        key = f"{user_id}/{chapter_name}/audio/narration.mp3"
        self.s3_client.upload_fileobj(self.projects_bucket, key, BytesIO(audio_data))
        return key

    def get_manifest_key(self, user_id: str, chapter_name: str) -> str:
        """Generate manifest key for given user and chapter."""
        return f"{user_id}/{chapter_name}/audio/manifest.json"

    def get_narration_key(self, user_id: str, chapter_name: str) -> str:
        """Generate narration key for given user and chapter."""
        return f"{user_id}/{chapter_name}/audio/narration.mp3"

    def manifest_exists(self, user_id: str, chapter_name: str) -> bool:
        """Check if manifest exists for the given user and chapter."""
        manifest_key = self.get_manifest_key(user_id, chapter_name)
        return bool(self.s3_client.list_files(self.projects_bucket, manifest_key))

    def get_manifest(self, user_id: str, chapter_name: str) -> Optional[Dict[str, Any]]:
        """Retrieve manifest data if it exists."""
        if not self.manifest_exists(user_id, chapter_name):
            return None

        manifest_key = self.get_manifest_key(user_id, chapter_name)
        manifest_data = self.s3_client.get_file(self.projects_bucket, manifest_key)
        return json.loads(manifest_data.decode("utf-8"))

    def upload_manifest(
        self, user_id: str, chapter_name: str, manifest_data: Dict[str, Any]
    ) -> str:
        """Upload manifest to S3 and return the key."""
        manifest_key = self.get_manifest_key(user_id, chapter_name)
        self.s3_client.upload_fileobj(
            self.projects_bucket,
            manifest_key,
            BytesIO(json.dumps(manifest_data).encode("utf-8")),
        )
        return manifest_key

    def get_audio_files(self, keys: List[str]) -> List[bytes]:
        """Retrieve multiple audio files by their S3 keys."""
        return [self.s3_client.get_file(self.projects_bucket, key) for key in keys]

    def create_manifest_data(
        self, user_id: str, chapter_name: str, segment_ids: List[str]
    ) -> Dict[str, Any]:
        """Create manifest data structure."""
        narration_key = self.get_narration_key(user_id, chapter_name)

        manifest_segments = [
            {
                "id": seg_id,
                "index": idx,
                "key": f"{user_id}/{chapter_name}/audio/segments/{seg_id}.mp3",
            }
            for idx, seg_id in enumerate(segment_ids)
        ]

        return {
            "narration": {"key": narration_key},
            "segments": manifest_segments,
        }
