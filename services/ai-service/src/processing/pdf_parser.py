"""
PDF Parser Module
Handles extraction of text from PDF files with multilingual support (Arabic/English)
"""

import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts and returns text from the PDF at the given path, preserving page breaks as two newline separators.
    
    Parameters:
        pdf_path (str): Path to the PDF file to extract.
    
    Returns:
        str: Concatenated text extracted from all pages, with pages separated by two newline characters.
    
    Raises:
        FileNotFoundError: If the file at `pdf_path` does not exist.
        ValueError: If no text could be extracted from the PDF.
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
            except Exception:
                continue
    
    if not text_content:
        raise ValueError(f"No text could be extracted from PDF: {pdf_path}")
    
    return "\n\n".join(text_content)