#!/usr/bin/env python3
"""
Test script to validate the download_model.py imports and basic logic.
"""

import sys
import os
from pathlib import Path

# Add paths to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "aws"))
sys.path.insert(0, str(Path(__file__).parent.parent / "types"))

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from tta_aws.s3 import S3Client
        print("✓ S3Client import successful")
        
        # Test S3Client instantiation
        client = S3Client()
        print("✓ S3Client instantiation successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_download_script_syntax():
    """Test that the download script has valid syntax."""
    try:
        import download_model
        print("✓ Download script syntax is valid")
        
        # Check that the main function exists
        if hasattr(download_model, 'download_model_file'):
            print("✓ download_model_file function exists")
            return True
        else:
            print("✗ download_model_file function not found")
            return False
    except Exception as e:
        print(f"✗ Download script syntax error: {e}")
        return False

if __name__ == "__main__":
    try:
        print("Testing imports...")
        imports_ok = test_imports()
        
        print("\nTesting download script...")
        script_ok = test_download_script_syntax()
        
        if imports_ok and script_ok:
            print("\n✓ All tests passed")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Test error: {e}")
        sys.exit(1)