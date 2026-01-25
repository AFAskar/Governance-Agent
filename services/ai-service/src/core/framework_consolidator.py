"""
Framework Consolidator Module
Extracts controls from multiple PDFs in parallel.
"""

from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from src.processing import extract_text_from_pdf
from src.core.framework_extractor import extract_controls_from_framework


def extract_controls_from_pdfs(
    pdf_paths_list: List[str], framework_name: str
) -> List[List[Dict[str, Any]]]:
    """
    Extract controls from multiple PDFs in parallel.
    Each PDF gets one LLM call.

    Args:
        pdf_paths_list: List of PDF file paths
        framework_name: Name of the framework

    Returns:
        List of controls arrays (one per PDF)
    """

    MAX_RETRIES = 2

    def extract_pdf(pdf_path: str):
        """Extract controls from a single PDF. Retries with fallback prompt if empty."""
        try:
            pdf_text = extract_text_from_pdf(pdf_path)
            controls_json = extract_controls_from_framework(pdf_text, framework_name)
            controls = controls_json.get("controls", [])
            retries = 0
            while len(controls) == 0 and retries < MAX_RETRIES:
                retries += 1
                print(f"Empty controls for {pdf_path}, retry {retries}/{MAX_RETRIES} with fallback prompt")
                controls_json = extract_controls_from_framework(
                    pdf_text, framework_name, use_fallback_prompt=True
                )
                controls = controls_json.get("controls", [])
            print(f"Controls extracted from {pdf_path}")
            return controls
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            return []

    with ThreadPoolExecutor(max_workers=len(pdf_paths_list)) as executor:
        controls_arrays = list(executor.map(extract_pdf, pdf_paths_list))

    return controls_arrays
