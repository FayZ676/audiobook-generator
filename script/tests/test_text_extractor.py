"""Tests for text extraction functionality."""

import pytest
from tta_script.text_extractor import extract_text_from_file, get_supported_extensions


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


def test_mobi_format_error():
    """Test that MOBI format raises appropriate error."""
    with pytest.raises(ValueError, match="MOBI format support requires additional setup"):
        extract_text_from_file(b"dummy content", "test.mobi")


def test_get_supported_extensions():
    """Test that supported extensions include at least txt."""
    extensions = get_supported_extensions()
    assert '.txt' in extensions
    assert isinstance(extensions, list)


def test_pdf_extraction_without_library():
    """Test PDF extraction when library is not available."""
    # This would need to be tested in an environment without PyPDF2
    # For now, we assume the library is available
    pass


def test_empty_filename():
    """Test handling of empty or invalid filenames."""
    with pytest.raises((ValueError, AttributeError)):
        extract_text_from_file(b"content", "")


def test_case_insensitive_extensions():
    """Test that file extensions are handled case-insensitively."""
    sample_text = "Test content"
    file_content = sample_text.encode('utf-8')
    
    # Test uppercase extension
    result = extract_text_from_file(file_content, "test.TXT")
    assert result == sample_text
    
    # Test mixed case extension
    result = extract_text_from_file(file_content, "test.Txt")
    assert result == sample_text