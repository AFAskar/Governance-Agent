"""
Utilities Module
Handles per-PDF extraction saves, input paths, and RAG helpers.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _project_root() -> Path:
    """
    Resolve the project root directory for this module.
    
    Returns:
        Path: The filesystem path to the project root (three parent directories above this file).
    """
    return Path(__file__).parent.parent.parent


def save_extraction_json(
    framework_name: str,
    pdf_path: str,
    controls_json: Dict[str, Any],
    custom_name: Optional[str] = None,
) -> Path:
    """
    Save extracted controls for a single PDF as JSON under config/frameworks/{framework_name}/.

    Filename is custom_name (if provided) or the PDF stem + .json (e.g. section-a.pdf -> section-a.json).

    Args:
        framework_name: Name of the framework (used for directory name)
        pdf_path: Path to the source PDF (used for filename when custom_name is not set)
        controls_json: Dictionary with framework_name and controls
        custom_name: Optional name for the JSON file (e.g. section name). If set, used instead of PDF stem.

    Returns:
        Path to the written JSON file
    """
    project_root = _project_root()
    base_dir = project_root / "config" / "frameworks"
    framework_dir = base_dir / framework_name
    framework_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(custom_name).name if custom_name else Path(pdf_path).stem
    out_path = framework_dir / f"{stem}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(controls_json, f, indent=2, ensure_ascii=False)
    return out_path


def get_input_paths() -> Dict[str, Path]:
    """
    Return standard project input directories.
    
    Returns:
        Mapping of input directory names to their project-relative Paths:
        - `frameworks`: Path to data/inputs/frameworks
        - `applicants`: Path to data/inputs/applicants
        - `vector_db`: Path to data/inputs/vector_db
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
    
    If the framework directory does not exist, returns an empty list. Files that cannot be opened or parsed are skipped.
    
    Returns:
        List[Tuple[str, Dict[str, Any]]]: A list of (stem, parsed_json) tuples where `stem` is the filename without the `.json` extension.
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
    Locate PDF files to use as input for the vector database for a given framework.
    
    Searches data/inputs/vector_db/{framework_name} for files with extensions `.pdf` or `.PDF` and returns those if any are present; otherwise returns PDFs from data/inputs/vector_db (flat). Returned paths are sorted and may be empty.
    
    Parameters:
        framework_name (str): Framework subdirectory name to prefer under data/inputs/vector_db.
    
    Returns:
        List[Path]: A list of Path objects pointing to found PDF files; may be empty.
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