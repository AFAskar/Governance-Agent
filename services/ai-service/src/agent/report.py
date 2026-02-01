"""
Report generation: comprehensive report from file_evaluations and mimic_json; save PDF.
"""

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _project_root() -> Path:
    return Path(__file__).parent.parent.parent


def build_report_pdf(state: dict[str, Any]) -> str:
    """
    Build a comprehensive report PDF from state (file_evaluations, mimic_json, evaluation_id).
    Saves to data/reports/{evaluation_id}.pdf. Returns the path (str).
    """
    evaluation_id = state.get("evaluation_id") or "unknown"
    framework_name = state.get("framework_name") or ""
    file_evaluations = state.get("file_evaluations") or []
    mimic_json = state.get("mimic_json") or {}

    root = _project_root()
    reports_dir = root / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{evaluation_id}.pdf"

    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Compliance Evaluation Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Evaluation ID: {evaluation_id}", styles["Normal"]))
    story.append(Paragraph(f"Framework: {framework_name}", styles["Normal"]))
    story.append(Spacer(1, 24))

    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(Paragraph(
        f"Total files evaluated: {len(file_evaluations)}. "
        "See per-file assessments below.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Control IDs per file (mimic JSON)", styles["Heading2"]))
    inner = mimic_json.get(framework_name, {})
    for field_id, ids_str in sorted(inner.items()):
        story.append(Paragraph(f"{field_id}: {ids_str}", styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Per-file assessments", styles["Heading1"]))
    for i, ev in enumerate(file_evaluations, 1):
        field_id = ev.get("field_id") or f"field_{i}"
        story.append(Paragraph(f"File {i} (Field: {field_id})", styles["Heading2"]))
        control_decisions = ev.get("control_decisions")
        if isinstance(control_decisions, list) and control_decisions:
            # Render table: Control ID | Decision | Rationale
            # Use Paragraph for cells so text wraps instead of overflowing
            def _cell(text: str, style_name: str = "Normal") -> Paragraph:
                escaped = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
                return Paragraph(escaped, styles[style_name])

            rows = [[_cell("Control ID", "Heading2"), _cell("Decision", "Heading2"), _cell("Rationale", "Heading2")]]
            for cd in control_decisions:
                cid = _cell(str(cd.get("control_id", "")))
                decision = _cell(str(cd.get("decision", "")))
                rationale = _cell(str(cd.get("rationale", "")))
                rows.append([cid, decision, rationale])
            # Rationale column gets most width; total ~420pt fits A4
            t = Table(rows, colWidths=[70, 70, 270])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))
        summary = ev.get("summary") or ev.get("evaluation") or ""
        if summary:
            text = summary if len(summary) <= 2000 else summary[:2000] + "..."
            story.append(Paragraph(text.replace("\n", "<br/>"), styles["Normal"]))
        elif not control_decisions:
            text = str(ev)
            if len(text) > 2000:
                text = text[:2000] + "..."
            story.append(Paragraph(text.replace("\n", "<br/>"), styles["Normal"]))
        story.append(Spacer(1, 8))

    doc.build(story)
    return str(path)
