"""
Dispatcher: given file path (and optional extension), call the right parser and return extracted text.
"""

from pathlib import Path

from .pdf_parser import extract_text_from_pdf
from .tabular_parser import extract_text_from_tabular
from .pptx_parser import extract_text_from_pptx
from .docx_parser import extract_text_from_docx


def extract_text_from_file(path: str, extension: str | None = None) -> str:
    """
    Dispatch by extension to the appropriate parser. Returns extracted text.
    Supported: .pdf, .csv, .xlsx, .xls, .pptx, .docx.
    """
    ext = (extension or Path(path).suffix).lower().lstrip(".")
    if ext == "pdf":
        return extract_text_from_pdf(path)
    if ext in ("csv", "xlsx", "xls"):
        return extract_text_from_tabular(path)
    if ext == "pptx":
        return extract_text_from_pptx(path)
    if ext == "docx":
        return extract_text_from_docx(path)
    raise ValueError(f"Unsupported file extension: {ext}")
