"""Tests for text extraction functionality."""

import io
import pytest
from unittest.mock import patch, MagicMock
from tta_service.text_extractor import extract_text_from_file


def test_txt_extraction():
    """Test extraction from txt files."""
    sample_text = "This is a test document.\n\nWith multiple paragraphs."
    file_content = sample_text.encode('utf-8')
    result = extract_text_from_file(file_content, "test.txt")
    assert result == sample_text


def test_pdf_extraction():
    """Test extraction from PDF files."""
    # Mock PyPDF2 functionality
    with patch('tta_service.text_extractor.PyPDF2.PdfReader') as mock_reader:
        # Setup mock
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "This is PDF content"
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page]
        mock_reader.return_value = mock_reader_instance
        
        # Test PDF extraction
        pdf_content = b"fake pdf content"
        result = extract_text_from_file(pdf_content, "test.pdf")
        
        # Verify the result
        assert "This is PDF content" in result
        mock_reader.assert_called_once()


def test_epub_extraction():
    """Test extraction from EPUB files."""
    # Mock ebooklib functionality
    with patch('tta_service.text_extractor.epub.read_epub') as mock_read_epub:
        # Setup mock book
        mock_book = MagicMock()
        mock_item = MagicMock()
        mock_item.get_type.return_value = 9  # ITEM_DOCUMENT
        mock_item.get_content.return_value = b'<html><body><h1>Test Chapter</h1><p>This is EPUB content</p></body></html>'
        mock_book.get_items.return_value = [mock_item]
        mock_read_epub.return_value = mock_book
        
        # Test EPUB extraction
        epub_content = b"fake epub content"
        result = extract_text_from_file(epub_content, "test.epub")
        
        # Verify the result (HTML tags should be removed)
        assert "Test Chapter" in result
        assert "This is EPUB content" in result
        mock_read_epub.assert_called_once()


def test_docx_extraction():
    """Test extraction from DOCX files."""
    # Mock python-docx functionality
    with patch('tta_service.text_extractor.Document') as mock_document:
        # Setup mock document
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "This is DOCX content"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "Another paragraph in DOCX"
        
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_paragraph1, mock_paragraph2]
        mock_document.return_value = mock_doc_instance
        
        # Test DOCX extraction
        docx_content = b"fake docx content"
        result = extract_text_from_file(docx_content, "test.docx")
        
        # Verify the result
        assert "This is DOCX content" in result
        assert "Another paragraph in DOCX" in result
        mock_document.assert_called_once()


def test_case_insensitive_extensions():
    """Test that file extensions are handled case-insensitively."""
    sample_text = "Test content"
    
    # Test uppercase extension
    file_content = sample_text.encode('utf-8')
    result = extract_text_from_file(file_content, "test.TXT")
    assert result == sample_text
    
    # Test mixed case extension
    result = extract_text_from_file(file_content, "test.Txt")
    assert result == sample_text


def test_pdf_multiple_pages():
    """Test PDF extraction with multiple pages."""
    with patch('tta_service.text_extractor.PyPDF2.PdfReader') as mock_reader:
        # Setup mock with multiple pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        mock_reader_instance = MagicMock()
        mock_reader_instance.pages = [mock_page1, mock_page2]
        mock_reader.return_value = mock_reader_instance
        
        # Test extraction
        result = extract_text_from_file(b"fake pdf", "test.pdf")
        
        # Verify both pages are included and separated properly
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        # Pages should be separated by double newlines
        assert "Page 1 content\n\nPage 2 content" == result


def test_epub_multiple_chapters():
    """Test EPUB extraction with multiple chapters."""
    with patch('tta_service.text_extractor.epub.read_epub') as mock_read_epub:
        # Setup mock book with multiple items
        mock_item1 = MagicMock()
        mock_item1.get_type.return_value = 9  # ITEM_DOCUMENT
        mock_item1.get_content.return_value = b'<html><body><h1>Chapter 1</h1><p>First chapter content</p></body></html>'
        
        mock_item2 = MagicMock()
        mock_item2.get_type.return_value = 9  # ITEM_DOCUMENT
        mock_item2.get_content.return_value = b'<html><body><h1>Chapter 2</h1><p>Second chapter content</p></body></html>'
        
        mock_book = MagicMock()
        mock_book.get_items.return_value = [mock_item1, mock_item2]
        mock_read_epub.return_value = mock_book
        
        # Test extraction
        result = extract_text_from_file(b"fake epub", "test.epub")
        
        # Verify both chapters are included
        assert "Chapter 1" in result
        assert "First chapter content" in result
        assert "Chapter 2" in result
        assert "Second chapter content" in result


def test_docx_empty_paragraphs_skipped():
    """Test that empty paragraphs in DOCX are skipped."""
    with patch('tta_service.text_extractor.Document') as mock_document:
        # Setup mock with empty and non-empty paragraphs
        mock_paragraph1 = MagicMock()
        mock_paragraph1.text = "Content paragraph"
        mock_paragraph2 = MagicMock()
        mock_paragraph2.text = "   "  # Whitespace only
        mock_paragraph3 = MagicMock()
        mock_paragraph3.text = ""  # Empty
        mock_paragraph4 = MagicMock()
        mock_paragraph4.text = "Another content paragraph"
        
        mock_doc_instance = MagicMock()
        mock_doc_instance.paragraphs = [mock_paragraph1, mock_paragraph2, mock_paragraph3, mock_paragraph4]
        mock_document.return_value = mock_doc_instance
        
        # Test extraction
        result = extract_text_from_file(b"fake docx", "test.docx")
        
        # Only non-empty paragraphs should be included
        assert "Content paragraph" in result
        assert "Another content paragraph" in result
        # Empty paragraphs should not create extra spacing
        assert result == "Content paragraph\n\nAnother content paragraph"


def test_unsupported_format():
    """Test handling of unsupported file formats."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text_from_file(b"dummy content", "test.xyz")