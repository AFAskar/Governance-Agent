"""
LangGraph evaluation graph: file processing -> mimic JSON -> file evaluation loop -> report.
"""

import json
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.messages import RemoveMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from .state import EvaluationState
from .groq_client import get_groq_llm
from .tools import get_tool_schemas, execute_tool
from .report import build_report_pdf

def _file_processing_node(state: EvaluationState) -> dict[str, Any]:
    """Extract text for all files; set state.files with path, extracted_text, field_id."""
    from src.processing import extract_text_from_file

    files = state.get("files") or []
    if not files:
        return {"errors": (state.get("errors") or []) + ["No files in state"]}
    result = []
    for i, f in enumerate(files):
        path = f.get("path") or ""
        field_id = f.get("field_id") or f"field_{i + 1}"
        try:
            text = extract_text_from_file(path)
        except Exception as e:
            text = f"[Extraction error: {e}]"
        result.append({"path": path, "extracted_text": text, "field_id": field_id})
    return {
        "files": result,
        "current_file_index": 0,
        "file_evaluations": [],
    }


def _mimic_json_node(state: EvaluationState) -> dict[str, Any]:
    """Ensure mimic_json is in state (already set by run.py from client or inference)."""
    return {}


def _build_file_prompt(state: EvaluationState) -> str:
    """Build the human prompt for the current file evaluation."""
    idx = state.get("current_file_index", 0)
    files = state.get("files") or []
    if idx >= len(files):
        return ""
    f = files[idx]
    field_id = f.get("field_id", f"field_{idx + 1}")
    text = (f.get("extracted_text") or "")[:15000]
    fw = state.get("framework_name", "")
    total = len(files)
    return (
        f"You are evaluating file {idx + 1} of {total} for framework '{fw}'.\n"
        f"Field ID for this file: {field_id}.\n\n"
        "## Tool usage (follow strictly)\n"
        f"1. Call get_control_ids_for_file once with field_id='{field_id}' to get the control IDs for this file.\n"
        "2. For EACH control ID returned, call retrieve_control_details once—one control_id per call. Do NOT pass multiple IDs.\n"
        "3. Use the returned description, calculation, threshold, and scale from each control to understand what it requires.\n\n"
        "## Control types and decision semantics\n"
        "- If a control has a non-empty 'scale' field (e.g. Leader, Excellent, Good, Fair, Low, Unacceptable): use those levels for your decision.\n"
        "- If a control has an empty 'scale' (policy/requirement): use 'Compliant' or 'Not Compliant'.\n\n"
        "## Output format (required)\n"
        "After retrieving and evaluating all controls, respond with JSON only (no extra text):\n"
        '{"control_decisions": [{"control_id": "DG.1.1", "decision": "Compliant", "rationale": "..."}, ...], '
        '"summary": "1-2 paragraph overall assessment of the file against all controls."}\n'
        "decision must match control type: use scale levels (Leader, Excellent, Good, Fair, Low, Unacceptable) when scale exists; otherwise Compliant or Not Compliant.\n\n"
        f"## File content to evaluate\n\n{text}"
    )


def _file_eval_agent_node(state: EvaluationState) -> dict[str, Any]:
    """Run the LLM for the current file; if first time for this file, set HumanMessage."""
    messages = list(state.get("messages") or [])
    # Start of a new file (messages cleared by file_eval_done): set prompt
    if not messages:
        prompt = _build_file_prompt(state)
        if not prompt:
            return {"errors": (state.get("errors") or []) + ["No file at index"]}
        messages = [HumanMessage(content=prompt)]
    llm = get_groq_llm().bind_tools(get_tool_schemas())
    response = llm.invoke(messages)
    # add_messages reducer appends; when starting we need HumanMessage + AIMessage in one update
    if len(messages) == 1 and isinstance(messages[0], HumanMessage):
        return {"messages": messages + [response]}
    return {"messages": [response]}


def _should_continue_tools(state: EvaluationState) -> Literal["tools", "file_eval_done"]:
    """If last message has tool_calls, go to tools; else file_eval_done."""
    messages = state.get("messages") or []
    if not messages:
        return "file_eval_done"
    last = messages[-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        return "tools"
    return "file_eval_done"


def _file_eval_tools_node(state: EvaluationState) -> dict[str, Any]:
    """Execute tools with access to state (for get_control_ids_for_file)."""
    messages = list(state.get("messages") or [])
    last = messages[-1] if messages else None
    if not isinstance(last, AIMessage) or not getattr(last, "tool_calls", None):
        return {}
    tool_messages = []
    for tc in last.tool_calls:
        name = tc.get("name", "")
        args = tc.get("args") or {}
        tid = tc.get("id", "")
        try:
            result = execute_tool(dict(state), name, args)
            content = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
        except Exception as e:
            content = str(e)
        tool_messages.append(ToolMessage(content=content, tool_call_id=tid))
    return {"messages": tool_messages}


def _file_eval_done_node(state: EvaluationState) -> dict[str, Any]:
    """Append evaluation from last message to file_evaluations; increment current_file_index; clear messages."""
    messages = state.get("messages") or []
    evaluations = list(state.get("file_evaluations") or [])
    files = state.get("files") or []
    idx = state.get("current_file_index", 0)
    field_id = files[idx].get("field_id", f"field_{idx + 1}") if idx < len(files) else f"field_{idx + 1}"
    content = ""
    if messages:
        last = messages[-1]
        if isinstance(last, AIMessage) and hasattr(last, "content") and last.content:
            content = last.content
    # Strip markdown code fences if present
    content_stripped = content.strip()
    if content_stripped.startswith("```"):
        lines = content_stripped.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content_stripped = "\n".join(lines)
    else:
        content_stripped = content
    # Try to parse as structured JSON
    try:
        parsed = json.loads(content_stripped)
        if isinstance(parsed, dict) and isinstance(parsed.get("control_decisions"), list) and parsed["control_decisions"]:
            evaluations.append({
                "file_index": idx,
                "field_id": field_id,
                "control_decisions": parsed["control_decisions"],
                "summary": parsed.get("summary", ""),
            })
        else:
            evaluations.append({"file_index": idx, "field_id": field_id, "summary": content})
    except (json.JSONDecodeError, TypeError):
        evaluations.append({"file_index": idx, "field_id": field_id, "summary": content})
    return {
        "file_evaluations": evaluations,
        "current_file_index": idx + 1,
        "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
    }


def _more_files(state: EvaluationState) -> Literal["file_eval_agent", "report"]:
    """If more files remain, next file; else report."""
    files = state.get("files") or []
    if (state.get("current_file_index") or 0) < len(files):
        return "file_eval_agent"
    return "report"


def _report_node(state: EvaluationState) -> dict[str, Any]:
    """Build comprehensive report PDF; set report_path."""
    path = build_report_pdf(dict(state))
    return {"report_path": path}


def build_evaluation_graph() -> StateGraph:
    """Build and compile the LangGraph evaluation graph."""
    workflow = StateGraph(EvaluationState)

    workflow.add_node("file_processing", _file_processing_node)
    workflow.add_node("mimic_json", _mimic_json_node)
    workflow.add_node("file_eval_agent", _file_eval_agent_node)
    workflow.add_node("file_eval_tools", _file_eval_tools_node)
    workflow.add_node("file_eval_done", _file_eval_done_node)
    workflow.add_node("report", _report_node)

    workflow.add_edge(START, "file_processing")
    workflow.add_edge("file_processing", "mimic_json")
    workflow.add_edge("mimic_json", "file_eval_agent")
    workflow.add_conditional_edges(
        "file_eval_agent",
        _should_continue_tools,
        {"tools": "file_eval_tools", "file_eval_done": "file_eval_done"},
    )
    workflow.add_edge("file_eval_tools", "file_eval_agent")
    workflow.add_conditional_edges("file_eval_done", _more_files, {"file_eval_agent": "file_eval_agent", "report": "report"})
    workflow.add_edge("report", END)

    return workflow.compile()