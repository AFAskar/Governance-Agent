"""
Utilities Module
Handles per-PDF extraction saves, input paths, and RAG helpers.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple


def _project_root() -> Path:
    return Path(__file__).parent.parent.parent


def save_extraction_json(
    framework_name: str, pdf_path: str, controls_json: Dict[str, Any]
) -> Path:
    """
    Save extracted controls for a single PDF as JSON under config/frameworks/{framework_name}/.

    Filename is the PDF stem + .json (e.g. section-a.pdf -> section-a.json).

    Args:
        framework_name: Name of the framework (used for directory name)
        pdf_path: Path to the source PDF (used for filename)
        controls_json: Dictionary with framework_name and controls

    Returns:
        Path to the written JSON file
    """
    project_root = _project_root()
    base_dir = project_root / "config" / "frameworks"
    framework_dir = base_dir / framework_name
    framework_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(pdf_path).stem
    out_path = framework_dir / f"{stem}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(controls_json, f, indent=2, ensure_ascii=False)
    return out_path


def get_input_paths() -> Dict[str, Path]:
    """
    Get standard input directory paths.

    Returns:
        Dictionary with paths:
        - frameworks: Path to framework PDFs directory
        - applicants: Path to applicant PDFs directory
        - vector_db: Path to vector DB input PDFs directory
    """
    project_root = _project_root()
    return {
        "frameworks": project_root / "data" / "inputs" / "frameworks",
        "applicants": project_root / "data" / "inputs" / "applicants",
        "vector_db": project_root / "data" / "inputs" / "vector_db",
    }


def list_framework_jsons(framework_name: str) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Load all JSON files for a framework from config/frameworks/{framework_name}/.

    Returns:
        List of (stem, parsed_json) tuples. Stem = filename without .json (e.g. PoliciesEn-1).
    """
    base = _project_root() / "config" / "frameworks" / framework_name
    if not base.is_dir():
        return []
    out: List[Tuple[str, Dict[str, Any]]] = []
    for p in sorted(base.glob("*.json")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            out.append((p.stem, data))
        except Exception:
            continue
    return out


def get_vector_db_pdf_paths(framework_name: str) -> List[Path]:
    """
    PDF paths used as input for the vector DB. Looks in data/inputs/vector_db/.

    Prefers vector_db/{framework_name}/*.pdf. If that dir has no PDFs, falls back to
    vector_db/*.pdf (flat).
    """
    paths = get_input_paths()
    vdb = paths["vector_db"]
    sub = vdb / framework_name
    if sub.is_dir():
        pdfs = sorted(sub.glob("*.pdf")) + sorted(sub.glob("*.PDF"))
        if pdfs:
            return pdfs
    pdfs = sorted(vdb.glob("*.pdf")) + sorted(vdb.glob("*.PDF"))
    return pdfs
