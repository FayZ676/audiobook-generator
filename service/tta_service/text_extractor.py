"""Text extraction utilities for text files."""

from pathlib import Path


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from text files.
    
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
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")