"""
Entry point: persist uploaded files, build state, run LangGraph, return state (mimic_json, report_path, file_evaluations).
"""

import logging
import re
import uuid
from pathlib import Path
from typing import Any

from src.utils import list_framework_jsons

from .graph import build_evaluation_graph
from .mimic_json import build_mimic_json
from .state import EvaluationState

logger = logging.getLogger(__name__)

# LangGraph steps consumed per file: agent + done + up to ~14 tool round-trips
# (each round-trip is one tools node + one agent node). Sized generously so a
# multi-file evaluation never trips the default recursion limit of 25.
_GRAPH_STEPS_PER_FILE = 30
_GRAPH_STEPS_BASE = 20


def _project_root() -> Path:
    return Path(__file__).parent.parent.parent


def _domain_control_ids(framework_name: str) -> dict[str, str]:
    """
    Map each framework section (JSON file stem, e.g. '1_Data_Governance') to the
    comma-separated control IDs it contains.

    Sections are created by the framework setup endpoint, which saves one JSON
    per section under config/frameworks/{framework_name}/{section_name}.json.
    """
    mapping: dict[str, str] = {}
    for stem, data in list_framework_jsons(framework_name):
        ids = [
            str(c["id"]).strip()
            for c in data.get("controls", [])
            if isinstance(c, dict) and str(c.get("id", "")).strip()
        ]
        if ids:
            mapping[stem] = ",".join(ids)
    return mapping


def resolve_control_ids(framework_name: str, domain_ids: list[str]) -> list[str]:
    """
    Resolve each domain ID to the comma-separated control IDs of that framework
    section. Falls back to the raw domain ID when no section JSON exists, so
    evaluations still run against frameworks that were indexed differently.
    """
    mapping = _domain_control_ids(framework_name)
    resolved: list[str] = []
    for domain_id in domain_ids:
        control_ids = mapping.get(domain_id, "")
        if control_ids:
            resolved.append(control_ids)
        else:
            if domain_id:
                logger.warning(
                    "No control IDs found for domain '%s' in framework '%s'; "
                    "passing the domain ID through unresolved",
                    domain_id,
                    framework_name,
                )
            resolved.append(domain_id)
    return resolved


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

    # Resolve each file's domain to its control IDs and build the mimic JSON
    if domain_ids:
        control_ids_per_file = resolve_control_ids(framework_name, domain_ids)
    else:
        control_ids_per_file = [""] * n
    field_control_ids = [
        (f"field_{i + 1}", ids) for i, ids in enumerate(control_ids_per_file)
    ]
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
    # The default LangGraph recursion limit (25 steps) is too small for
    # multi-file evaluations; size it to the number of files being processed.
    recursion_limit = _GRAPH_STEPS_BASE + _GRAPH_STEPS_PER_FILE * n
    final_state = graph.invoke(initial_state, config={"recursion_limit": recursion_limit})

    return {
        "evaluation_id": evaluation_id,
        "mimic_json": final_state.get("mimic_json", mimic_json),
        "report_path": final_state.get("report_path", ""),
        "file_evaluations": final_state.get("file_evaluations", []),
    }
