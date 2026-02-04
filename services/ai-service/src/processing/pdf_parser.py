"""
PDF Parser Module
Handles extraction of text from PDF files with multilingual support (Arabic/English)
"""

import logging

import pdfplumber
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file with support for multilingual content.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ValueError: If PDF is corrupted or cannot be read
    """
    pdf_path_obj = Path(pdf_path)
    
    if not pdf_path_obj.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            except Exception as e:
                logger.warning("Failed to extract text from page %d of %s: %s", page.page_number, pdf_path, e)
                continue
    
    if not text_content:
        raise ValueError(f"No text could be extracted from PDF: {pdf_path}")
    
    return "\n\n".join(text_content)
