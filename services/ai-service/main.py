"""
Main entry point for the Compliance Framework Extraction System.
CLI: extract controls from each PDF and save one JSON per PDF (no compose, no prompt).
Uses the same service layer as the API.
"""

import glob
from pathlib import Path

from src.services import FrameworkService
from src.utils import get_input_paths


def setup_framework(pdf_paths: str | list[str], framework_name: str) -> list[Path]:
    """
    Extract controls from each PDF and save one JSON per PDF under config/frameworks/{framework_name}/.

    Each file is named after the source PDF stem (e.g. section-a.pdf -> section-a.json).
    No composition or evaluation prompt generation.

    Args:
        pdf_paths: Single file path, list of files, or directory path
        framework_name: Name of the framework

    Returns:
        List of paths to the saved JSON files
    """
    if isinstance(pdf_paths, list):
        pdf_paths_list = pdf_paths
    else:
        p = Path(pdf_paths)
        if p.is_dir():
            pdf_paths_list = sorted(glob.glob(f"{pdf_paths}/*.pdf"))
        else:
            pdf_paths_list = [pdf_paths]

    if not pdf_paths_list:
        raise ValueError(f"No PDF files found: {pdf_paths}")

    pdf_sections = [(Path(p).stem, Path(p).read_bytes()) for p in pdf_paths_list]
    service = FrameworkService()
    result = service.setup_framework(framework_name=framework_name, pdf_sections=pdf_sections)

    project_root = Path(__file__).resolve().parent
    return [project_root / s["json_path"] for s in result["sections"]]


def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("Compliance Framework Extraction System")
    print("=" * 60)

    paths = get_input_paths()
    print("\nDirectory structure:")
    print(f"  Input PDFs (Frameworks): {paths['frameworks']}")
    print(f"  Input PDFs (Applicants): {paths['applicants']}")
    print("  Framework outputs: config/frameworks/")

    print("\nUsage:")
    print("   setup_framework('data/inputs/frameworks/<dir>', 'framework_name')")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    framework_path = "data/inputs/frameworks/NDI"
    framework_name = "NDI"
    setup_framework(framework_path, framework_name)
