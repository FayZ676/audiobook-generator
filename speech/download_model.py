#!/usr/bin/env python3
"""
Script to download the VOCOS model file from S3.
Used during Docker build to securely download the pytorch_model.bin file.
"""

import os
import sys
from pathlib import Path

# Add paths for local imports when not installed as packages
current_dir = Path(__file__).parent
if not hasattr(sys, '_called_from_test'):
    # In Docker build, these will be installed packages
    try:
        from tta_aws.s3 import S3Client
    except ImportError:
        # Fallback for local development/testing
        sys.path.insert(0, str(current_dir.parent / "aws"))
        sys.path.insert(0, str(current_dir.parent / "types"))
        from tta_aws.s3 import S3Client
else:
    # When called from test, import should already be set up
    from tta_aws.s3 import S3Client


def download_model_file():
    """Download the VOCOS pytorch_model.bin file from S3."""
    # Get bucket name from environment variable
    bucket_name = os.environ.get("MODEL_FILES_BUCKET", "tta-model-files")
    file_key = "vocos/pytorch_model.bin"
    
    # Create target directory
    target_dir = Path(__file__).parent / "tta_speech" / "vocos"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / "pytorch_model.bin"
    
    try:
        print(f"Downloading {file_key} from S3 bucket {bucket_name}...")
        
        # Initialize S3 client
        s3_client = S3Client()
        
        # Download file content
        file_content = s3_client.get_file(bucket_name, file_key)
        
        # Write to target file
        with open(target_file, "wb") as f:
            f.write(file_content)
        
        print(f"Successfully downloaded {file_key} to {target_file}")
        print(f"File size: {len(file_content)} bytes")
        
        return True
        
    except Exception as e:
        print(f"Error downloading model file: {e}", file=sys.stderr)
        print("Ensure that:", file=sys.stderr)
        print(f"1. S3 bucket '{bucket_name}' exists and contains the file '{file_key}'", file=sys.stderr)
        print("2. AWS credentials are properly configured", file=sys.stderr)
        print("3. The IAM user has permissions to access the bucket", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = download_model_file()
    sys.exit(0 if success else 1)