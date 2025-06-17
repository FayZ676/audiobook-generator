"""Tests for text extraction functionality."""

import pytest
from pathlib import Path
from tta_service.text_extractor import extract_text_from_file


def test_txt_extraction():
    """Test extraction from txt files."""
    sample_text = "This is a test document.\n\nWith multiple paragraphs."
    file_content = sample_text.encode('utf-8')
    result = extract_text_from_file(file_content, "test.txt")
    assert result == sample_text


def test_pdf_extraction():
    """Test extraction from PDF files."""
    # Load test PDF file
    test_file = Path(__file__).parent / "test_files" / "test.pdf"
    if not test_file.exists():
        pytest.skip("Test PDF file not found")
    
    with open(test_file, "rb") as f:
        pdf_content = f.read()
    
    result = extract_text_from_file(pdf_content, "test.pdf")
    assert "Test PDF Content" in result
    assert "This is a test PDF file" in result


def test_epub_extraction():
    """Test extraction from EPUB files."""
    # Load test EPUB file
    test_file = Path(__file__).parent / "test_files" / "test.epub"
    if not test_file.exists():
        pytest.skip("Test EPUB file not found")
    
    with open(test_file, "rb") as f:
        epub_content = f.read()
    
    result = extract_text_from_file(epub_content, "test.epub")
    assert "Test EPUB Content" in result
    assert "This is a test EPUB file" in result


def test_docx_extraction():
    """Test extraction from DOCX files."""
    # Load test DOCX file
    test_file = Path(__file__).parent / "test_files" / "test.docx"
    if not test_file.exists():
        pytest.skip("Test DOCX file not found")
    
    with open(test_file, "rb") as f:
        docx_content = f.read()
    
    result = extract_text_from_file(docx_content, "test.docx")
    assert "Test DOCX Content" in result
    assert "This is a test DOCX file" in result


def test_unsupported_format():
    """Test handling of unsupported file formats."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text_from_file(b"dummy content", "test.xyz")