"""Tests for text extraction functionality."""

import pytest
from tta_service.text_extractor import extract_text_from_file


def test_txt_extraction():
    """Test extraction from txt files."""
    sample_text = "This is a test document.\n\nWith multiple paragraphs."
    file_content = sample_text.encode('utf-8')
    result = extract_text_from_file(file_content, "test.txt")
    assert result == sample_text


def test_unsupported_format():
    """Test handling of unsupported file formats."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text_from_file(b"dummy content", "test.xyz")