"""
Agent tools: (1) get control IDs for this PDF from mimic JSON, (2) retrieve control details from vector DB.
Both are used by the LLM during file evaluation.
"""

from typing import Any

from src.rag import retrieve_control_details as rag_retrieve_control_details
from src.rag.retrieval import RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA

# Schema for get_control_ids_for_file (OpenAI-style for Groq)
GET_CONTROL_IDS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_control_ids_for_file",
        "description": (
            "Get the comma-separated control IDs assigned to this file/field from the mimic JSON. "
            "Returns a string like 'DG.1.1,DG.1.2,DSI.OE.01'. You must then call retrieve_control_details "
            "once for EACH control ID in that list to fetch rules and requirements from the vector DB. "
            "Do not call retrieve_control_details with multiple IDs—it accepts only one control_id per call."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "field_id": {
                    "type": "string",
                    "description": "The field identifier for this file (e.g. field_1, field_2, ..., field_15).",
                },
            },
            "required": ["field_id"],
        },
    },
}


def get_control_ids_for_file(state: dict[str, Any], field_id: str) -> str:
    """
    Read from state's mimic_json: return comma-separated control IDs for the given field_id.
    """
    mimic = state.get("mimic_json") or {}
    fw = state.get("framework_name") or ""
    return mimic.get(fw, {}).get(field_id, "")


def retrieve_control_details_multi(
    control_ids: str,
    framework_name: str,
    *,
    top_k_pdf: int = 5,
) -> dict[str, Any]:
    """
    Retrieve control details for multiple control IDs (comma-separated).
    Calls src.rag.retrieve_control_details for each and returns combined result.
    """
    ids = [x.strip() for x in control_ids.split(",") if x.strip()]
    controls = []
    for cid in ids:
        try:
            out = rag_retrieve_control_details(cid, framework_name, top_k_pdf=top_k_pdf)
            controls.append({"control_id": cid, **out})
        except Exception as e:
            controls.append(
                {"control_id": cid, "error": str(e), "json_cards": [], "pdf_chunks": []}
            )
    return {"controls": controls}


def get_tool_schemas() -> list[dict]:
    """Return list of tool schemas for binding to the LLM (Groq/OpenAI format)."""
    return [GET_CONTROL_IDS_TOOL_SCHEMA, RETRIEVE_CONTROL_DETAILS_TOOL_SCHEMA]


def execute_tool(state: dict[str, Any], name: str, args: dict[str, Any]) -> Any:
    """
    Execute a tool by name with the given args. State is used for get_control_ids_for_file.
    """
    if name == "get_control_ids_for_file":
        return get_control_ids_for_file(state, args["field_id"])
    if name == "retrieve_control_details":
        return rag_retrieve_control_details(
            args["control_id"],
            args["framework_name"],
            top_k_pdf=args.get("top_k_pdf", 5),
        )
    raise ValueError(f"Unknown tool: {name}")
