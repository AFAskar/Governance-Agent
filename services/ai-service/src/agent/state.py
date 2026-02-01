"""
LangGraph state for the evaluation agent.
"""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class EvaluationState(TypedDict, total=False):
    """State for the evaluation graph."""

    evaluation_id: str
    framework_name: str
    files: list[dict[str, Any]]  # [{path, extracted_text, field_id}, ...]
    mimic_json: dict[str, Any]  # { framework_name: { field_1: "id1,id2", ... } }
    current_file_index: int
    file_evaluations: list[dict[str, Any]]  # per-file assessment results
    report_path: str
    errors: list[str]
    # For agent node: messages (if using message-based LLM)
    messages: Annotated[list, add_messages]
