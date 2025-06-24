"""
Script to download the VOCOS model file from S3.
Used during Docker build to securely download the pytorch_model.bin file.
"""

import os
from pathlib import Path

from tta_aws.s3 import S3Client


def download_model_file():
    """Download the VOCOS pytorch_model.bin file from S3."""

    bucket_name = os.environ.get("MODEL_FILES_BUCKET", "tta-model-files")
    file_key = "pytorch_model.bin"

    target_dir = Path(__file__).parent / "tta_speech" / "vocos"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "pytorch_model.bin"

    s3_client = S3Client()
    file_content = s3_client.get_file(bucket_name, file_key)

    with open(target_file, "wb") as f:
        f.write(file_content)

    return True


if __name__ == "__main__":
    download_model_file()
