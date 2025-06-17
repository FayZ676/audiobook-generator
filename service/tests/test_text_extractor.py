"""Tests for text extraction functionality."""

import pytest
from tta_service.text_extractor import extract_text_from_file


def test_txt_extraction():
    """Test extraction from txt files."""
    sample_text = "This is a test document.\n\nWith multiple paragraphs."
    file_content = sample_text.encode('utf-8')
    result = extract_text_from_file(file_content, "test.txt")
    assert result == sample_text


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


def test_pdf_extraction_without_library():
    """Test PDF extraction shows helpful error when library not available."""
    with pytest.raises(ValueError, match="PyPDF2 is required for PDF support"):
        extract_text_from_file(b"dummy pdf content", "test.pdf")


def test_epub_extraction_without_library():
    """Test EPUB extraction shows helpful error when library not available."""
    with pytest.raises(ValueError, match="ebooklib is required for EPUB support"):
        extract_text_from_file(b"dummy epub content", "test.epub")


def test_docx_extraction_without_library():
    """Test DOCX extraction shows helpful error when library not available."""
    with pytest.raises(ValueError, match="python-docx is required for DOCX support"):
        extract_text_from_file(b"dummy docx content", "test.docx")


def test_unsupported_format():
    """Test handling of unsupported file formats."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text_from_file(b"dummy content", "test.xyz")