#!/usr/bin/env python3
"""
Helper script to upload the VOCOS model file to S3.
Run this script after deploying the CloudFormation template to upload the model file.

Usage:
    python upload_model_to_s3.py [bucket_name]

The script will:
1. Download pytorch_model.bin from HuggingFace
2. Upload it to the specified S3 bucket
"""

import os
import sys
import urllib.request
from pathlib import Path

# Add paths for local imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent / "aws"))
sys.path.insert(0, str(current_dir.parent / "types"))

from tta_aws.s3 import S3Client


def download_from_huggingface():
    """Download the model file from HuggingFace."""
    url = "https://huggingface.co/charactr/vocos-mel-24khz/resolve/main/pytorch_model.bin"
    temp_file = Path("/tmp/pytorch_model.bin")
    
    print(f"Downloading model file from {url}...")
    urllib.request.urlretrieve(url, temp_file)
    print(f"Downloaded to {temp_file}")
    
    return temp_file


def upload_to_s3(file_path, bucket_name):
    """Upload the model file to S3."""
    s3_client = S3Client()
    file_key = "vocos/pytorch_model.bin"
    
    print(f"Uploading {file_path} to s3://{bucket_name}/{file_key}...")
    
    with open(file_path, "rb") as f:
        result = s3_client.upload_fileobj(bucket_name, file_key, f)
    
    print(f"Successfully uploaded to {result}")
    return result


def main():
    """Main function to download and upload the model file."""
    # Get bucket name from command line or use default
    bucket_name = sys.argv[1] if len(sys.argv) > 1 else "tta-model-files"
    
    try:
        # Download from HuggingFace
        temp_file = download_from_huggingface()
        
        # Upload to S3
        s3_url = upload_to_s3(temp_file, bucket_name)
        
        # Clean up
        temp_file.unlink()
        
        print(f"\n✓ Successfully uploaded model file to {s3_url}")
        print("The model file is now ready for use in the Docker build process.")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python upload_model_to_s3.py [bucket_name]")
        print("If no bucket name is provided, 'tta-model-files' will be used.")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)