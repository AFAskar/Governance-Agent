"""
Entry point: persist uploaded files, build state, run LangGraph, return state (mimic_json, report_path, file_evaluations).
"""

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
    control_ids_per_file: list[str] | None = None,
) -> dict[str, Any]:
    """
    Run the evaluation agent: persist files, build mimic JSON, run graph, return final state.

    Args:
        framework_name: Framework name (e.g. NDI).
        files: List of (filename, bytes); 1 or more files.
        control_ids_per_file: List of comma-separated control ID strings (one per file).
            Must have the same length as files. Can be empty strings if not provided.

    Returns:
        dict with mimic_json, evaluation_id, report_path, file_evaluations.
    """
    if not files:
        raise ValueError("At least one file is required")
    n = len(files)
    if control_ids_per_file is not None and len(control_ids_per_file) != n:
        raise ValueError(f"control_ids_per_file has {len(control_ids_per_file)} entries but {n} files; they must match")

    evaluation_id = str(uuid.uuid4())
    root = _project_root()
    eval_dir = root / "data" / "evaluations" / evaluation_id
    eval_dir.mkdir(parents=True, exist_ok=True)

    # Persist files and build file list with path and field_id
    file_list = []
    for i, (filename, body) in enumerate(files):
        safe_name = (filename or f"file_{i+1}").replace("..", "_").strip() or f"file_{i+1}"
        path = eval_dir / safe_name
        path.write_bytes(body)
        field_id = f"field_{i + 1}"
        file_list.append({"path": str(path), "extracted_text": "", "field_id": field_id})

    # Build mimic JSON: from client control_ids (must match file count)
    if control_ids_per_file:
        field_control_ids = [(f"field_{i+1}", s.strip()) for i, s in enumerate(control_ids_per_file)]
    else:
        field_control_ids = [(f"field_{i+1}", "") for i in range(n)]
    mimic_json = build_mimic_json(framework_name, field_control_ids)

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
