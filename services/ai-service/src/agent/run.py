"""
Entry point: persist uploaded files, build state, run LangGraph, return state (mimic_json, report_path, file_evaluations).
"""

import re
import uuid
from pathlib import Path
from typing import Any

from .state import EvaluationState
from .graph import build_evaluation_graph
from .mimic_json import build_mimic_json


def _project_root() -> Path:
    return Path(__file__).parent.parent.parent


def run_evaluation_agent(
    framework_name: str,
    files: list[tuple[str, bytes]],
    domain_ids: list[str] | None = None,
) -> dict[str, Any]:
    """
    Run the evaluation agent: persist files, build mimic JSON, run graph, return final state.

    Args:
        framework_name: Framework name (e.g. NDI).
        files: List of (filename, bytes); 1 or more files.
        domain_ids: List of domain IDs (one per file). Each domain ID maps to a set of controls.
            Must have the same length as files if provided.

    Returns:
        dict with mimic_json, evaluation_id, report_path, file_evaluations.
    """
    if not files:
        raise ValueError("At least one file is required")
    n = len(files)
    if domain_ids is not None and len(domain_ids) != n:
        raise ValueError(f"domain_ids has {len(domain_ids)} entries but {n} files; they must match")

    evaluation_id = str(uuid.uuid4())
    root = _project_root()
    eval_dir = root / "data" / "evaluations" / evaluation_id
    eval_dir.mkdir(parents=True, exist_ok=True)

    # Persist files and build file list with path, field_id, and domain_id
    file_list = []
    for i, (filename, body) in enumerate(files):
        raw_name = Path(filename or f"file_{i+1}").name
        safe_name = re.sub(r"[^a-zA-Z0-9._\-]", "_", raw_name).lstrip(".") or f"file_{i+1}"
        path = eval_dir / safe_name
        path.write_bytes(body)
        field_id = f"field_{i + 1}"
        domain_id = domain_ids[i] if domain_ids else ""
        file_list.append({
            "path": str(path),
            "extracted_text": "",
            "field_id": field_id,
            "domain_id": domain_id,
        })

    # Build mimic JSON from domain_ids
    if domain_ids:
        field_domain_ids = [(f"field_{i+1}", d) for i, d in enumerate(domain_ids)]
    else:
        field_domain_ids = [(f"field_{i+1}", "") for i in range(n)]
    mimic_json = build_mimic_json(framework_name, field_domain_ids)

    initial_state: EvaluationState = {
        "evaluation_id": evaluation_id,
        "framework_name": framework_name,
        "files": file_list,
        "mimic_json": mimic_json,
        "current_file_index": 0,
        "file_evaluations": [],
        "messages": [],
    }

    graph = build_evaluation_graph()
    final_state = graph.invoke(initial_state)

    return {
        "evaluation_id": evaluation_id,
        "mimic_json": final_state.get("mimic_json", mimic_json),
        "report_path": final_state.get("report_path", ""),
        "file_evaluations": final_state.get("file_evaluations", []),
    }
