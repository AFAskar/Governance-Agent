"""
Report generation: comprehensive report from file_evaluations and mimic_json; save PDF.
"""

import logging
import re
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = logging.getLogger(__name__)

# Source documents and the rationales quoting them are frequently Arabic. The
# built-in Helvetica has no Arabic glyphs, so without a Unicode TTF the report
# silently renders those runs as black boxes.
_ARABIC_RE = re.compile(r"[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]")

_FONT_CANDIDATES = (
    ("Amiri", "/usr/share/fonts/truetype/hosny-amiri/Amiri-Regular.ttf"),
    ("Amiri", "/usr/share/fonts/truetype/amiri/Amiri-Regular.ttf"),
    ("NotoNaskh", "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"),
    ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)

_BODY_FONT = "Helvetica"
_BOLD_FONT = "Helvetica-Bold"


def _register_unicode_font() -> None:
    """Register the first available Arabic-capable TTF; keep Helvetica if none."""
    global _BODY_FONT, _BOLD_FONT
    if _BODY_FONT != "Helvetica":
        return
    for name, ttf in _FONT_CANDIDATES:
        if not Path(ttf).is_file():
            continue
        try:
            pdfmetrics.registerFont(TTFont(name, ttf))
        except Exception as e:  # pragma: no cover - depends on the image's fonts
            logger.warning("Could not register font %s from %s: %s", name, ttf, e)
            continue
        # These faces ship no separate bold; reusing the regular keeps headings
        # readable rather than falling back to a font without Arabic glyphs.
        _BODY_FONT = name
        _BOLD_FONT = name
        logger.info("Report font: %s (%s)", name, ttf)
        return
    logger.warning("No Arabic-capable font found; Arabic text in reports may not render.")


def _shape(text: str) -> str:
    """Reshape and bidi-reorder Arabic so ReportLab draws it correctly."""
    if not text or not _ARABIC_RE.search(text):
        return text
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        return get_display(arabic_reshaper.reshape(text))
    except Exception as e:  # pragma: no cover - optional dependency
        logger.warning("Arabic shaping unavailable, rendering raw text: %s", e)
        return text


def _markup(text: str) -> str:
    """Shape, XML-escape, and turn newlines into <br/> for a Paragraph."""
    lines = []
    for line in str(text).split("\n"):
        shaped = _shape(line)
        lines.append(shaped.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return "<br/>".join(lines)


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

    _register_unicode_font()

    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = getSampleStyleSheet()
    for style_name in ("Title", "Heading1", "Heading2", "Normal"):
        styles[style_name].fontName = _BOLD_FONT if style_name != "Normal" else _BODY_FONT
    story = []

    story.append(Paragraph("Compliance Evaluation Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Evaluation ID: {evaluation_id}", styles["Normal"]))
    story.append(Paragraph(_markup(f"Framework: {framework_name}"), styles["Normal"]))
    story.append(Spacer(1, 24))

    story.append(Paragraph("Executive Summary", styles["Heading1"]))
    story.append(
        Paragraph(
            f"Total files evaluated: {len(file_evaluations)}. See per-file assessments below.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 16))

    story.append(Paragraph("Control IDs per file (mimic JSON)", styles["Heading2"]))
    inner = mimic_json.get(framework_name, {})
    for field_id, ids_str in sorted(inner.items()):
        story.append(Paragraph(_markup(f"{field_id}: {ids_str}"), styles["Normal"]))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Per-file assessments", styles["Heading1"]))
    for i, ev in enumerate(file_evaluations, 1):
        field_id = ev.get("field_id") or f"field_{i}"
        story.append(Paragraph(_markup(f"File {i} (Field: {field_id})"), styles["Heading2"]))
        control_decisions = ev.get("control_decisions")
        if isinstance(control_decisions, list) and control_decisions:
            # Render table: Control ID | Decision | Rationale
            # Use Paragraph for cells so text wraps instead of overflowing
            def _cell(text: str, style_name: str = "Normal") -> Paragraph:
                return Paragraph(_markup(text), styles[style_name])

            rows = [
                [
                    _cell("Control ID", "Heading2"),
                    _cell("Decision", "Heading2"),
                    _cell("Rationale", "Heading2"),
                ]
            ]
            for cd in control_decisions:
                cid = _cell(str(cd.get("control_id", "")))
                decision = _cell(str(cd.get("decision", "")))
                rationale = _cell(str(cd.get("rationale", "")))
                rows.append([cid, decision, rationale])
            # Rationale column gets most width; total ~420pt fits A4
            t = Table(rows, colWidths=[70, 70, 270])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 0), (-1, 0), _BOLD_FONT),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("LEFTPADDING", (0, 0), (-1, -1), 6),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ]
                )
            )
            story.append(t)
            story.append(Spacer(1, 8))
        summary = ev.get("summary") or ev.get("evaluation") or ""
        if summary:
            text = summary if len(summary) <= 2000 else summary[:2000] + "..."
            story.append(Paragraph(_markup(text), styles["Normal"]))
        elif not control_decisions:
            text = str(ev)
            if len(text) > 2000:
                text = text[:2000] + "..."
            story.append(Paragraph(_markup(text), styles["Normal"]))
        story.append(Spacer(1, 8))

    try:
        doc.build(story)
    except Exception as e:
        logger.error("Failed to build report PDF at %s: %s", path, e)
        raise
    logger.info("Report generated: %s", path)
    return str(path)
