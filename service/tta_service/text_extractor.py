"""Text extraction utilities for multiple file formats."""

import io
from pathlib import Path
from typing import Union

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    ebooklib = None
    epub = None

try:
    from docx import Document
except ImportError:
    Document = None


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
    
    if file_extension == '.txt':
        return file_content.decode('utf-8')
    elif file_extension == '.pdf':
        return _extract_from_pdf(file_content)
    elif file_extension == '.epub':
        return _extract_from_epub(file_content)
    elif file_extension == '.docx':
        return _extract_from_docx(file_content)
    elif file_extension == '.mobi':
        # MOBI files require specialized tools like calibre
        # For now, we'll raise an error but this can be extended later
        raise ValueError("MOBI format support requires additional setup. Please convert to EPUB or PDF.")
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def _extract_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF files."""
    if PyPDF2 is None:
        raise ValueError("PyPDF2 is required for PDF support. Please install it.")
    
    pdf_file = io.BytesIO(file_content)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    text_content = []
    for page in pdf_reader.pages:
        text_content.append(page.extract_text())
    
    return '\n\n'.join(text_content)


def _extract_from_epub(file_content: bytes) -> str:
    """Extract text from EPUB files."""
    if ebooklib is None or epub is None:
        raise ValueError("ebooklib is required for EPUB support. Please install it.")
    
    epub_file = io.BytesIO(file_content)
    book = epub.read_epub(epub_file)
    
    text_content = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Parse HTML content and extract text
            content = item.get_content().decode('utf-8')
            # Simple HTML tag removal - this could be enhanced with BeautifulSoup
            import re
            text = re.sub(r'<[^>]+>', '', content)
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                text_content.append(text)
    
    return '\n\n'.join(text_content)


def _extract_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX files."""
    if Document is None:
        raise ValueError("python-docx is required for DOCX support. Please install it.")
    
    docx_file = io.BytesIO(file_content)
    doc = Document(docx_file)
    
    text_content = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_content.append(paragraph.text)
    
    return '\n\n'.join(text_content)


def get_supported_extensions() -> list[str]:
    """Get list of supported file extensions."""
    extensions = ['.txt']
    
    if PyPDF2 is not None:
        extensions.append('.pdf')
    if ebooklib is not None:
        extensions.append('.epub')
    if Document is not None:
        extensions.append('.docx')
    
    return extensions