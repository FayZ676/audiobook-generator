"""Text extraction utilities for multiple file formats."""

import io
import re
from pathlib import Path

import PyPDF2
import ebooklib
from ebooklib import epub
from docx import Document


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from various file formats.
    
    Args:
        file_content: The raw bytes of the file
        filename: The name of the file to determine the format
        
    Returns:
        Extracted text as a string
        
    Raises:
        ValueError: If the file format is not supported
    """
    file_extension = Path(filename).suffix.lower()
    
    match file_extension:
        case '.txt':
            return file_content.decode('utf-8')
        case '.pdf':
            return _extract_from_pdf(file_content)
        case '.epub':
            return _extract_from_epub(file_content)
        case '.docx':
            return _extract_from_docx(file_content)
        case _:
            raise ValueError(f"Unsupported file format: {file_extension}")


def _extract_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF files."""
    pdf_file = io.BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    text_content = []
    for page in pdf_reader.pages:
        text_content.append(page.extract_text())
    
    return '\n\n'.join(text_content)


def _extract_from_epub(file_content: bytes) -> str:
    """Extract text from EPUB files."""
    epub_file = io.BytesIO(file_content)
    book = epub.read_epub(epub_file)
    
    text_content = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse HTML content and extract text
            content = item.get_content().decode('utf-8')
            # Simple HTML tag removal - this could be enhanced with BeautifulSoup
            text = re.sub(r'<[^>]+>', '', content)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                text_content.append(text)
    
    return '\n\n'.join(text_content)


def _extract_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX files."""
    docx_file = io.BytesIO(file_content)
    doc = Document(docx_file)
    
    text_content = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_content.append(paragraph.text)
    
    return '\n\n'.join(text_content)