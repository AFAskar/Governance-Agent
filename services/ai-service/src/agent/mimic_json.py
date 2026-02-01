"""
Pure logic: build the DB-mimic dict { framework_name: { field_1: "id1,id2", ..., field_N: "..." } }.
"""

from typing import Any


def build_mimic_json(
    framework_name: str,
    field_control_ids: list[tuple[str, str]],
) -> dict[str, Any]:
    """
    Build the mimic JSON from framework name and list of (field_id, comma-separated control IDs).
    field_control_ids length must match the number of files (one entry per file).
    """
    if not field_control_ids:
        raise ValueError("At least one field/control_id pair is required")
    inner = {}
    for field_id, ids_str in field_control_ids:
        inner[field_id] = (ids_str or "").strip()
    return {framework_name: inner}
