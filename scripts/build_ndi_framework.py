#!/usr/bin/env python3
"""
Build the NDI framework catalog from the two official NDMO PDFs.

Why this exists instead of POST /api/v1/frameworks/setup:

  The setup endpoint sends a whole PDF through an LLM and asks for JSON back.
  PoliciesEn001.pdf is 173 pages holding 191 specifications; that answer does
  not fit in one response, and a truncated answer silently produces a framework
  with missing controls. Both PDFs are laid out as regular tables with labelled
  fields, so parsing them directly is exact, free, and takes seconds.

What it writes:

  config/frameworks/NDI/{domain_id}.json for each of the 12 domain IDs in
  apps/tanstack-start/src/lib/ndi-domains.ts, in the schema the evaluator reads
  (framework_name + controls[{id, description, calculation, threshold, scale}]).

  The filenames must equal the UI domain IDs exactly: resolve_control_ids()
  looks up config/frameworks/NDI/{domain_id}.json by that stem, and on a miss
  passes the domain ID through as if it were a control ID.

Usage:
  python scripts/build_ndi_framework.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import pdfplumber
except ImportError:
    sys.exit("pdfplumber is required: run this with services/ai-service/.venv/bin/python")

ROOT = Path(__file__).resolve().parent.parent
SERVICE = ROOT / "services" / "ai-service"
PDF_DIR = SERVICE / "data" / "inputs" / "frameworks" / "NDI"
OUT_DIR = SERVICE / "config" / "frameworks" / "NDI"

POLICIES_PDF = PDF_DIR / "PoliciesEn001.pdf"
OE_PDF = PDF_DIR / "OperationalExcellence-OE.pdf"

SPEC_ID_RE = re.compile(r"^([A-Z]{2,4})\.(\d+)\.(\d+)$")
OE_ID_RE = re.compile(r"^([A-Z]{2,4})\.OE\.(\d+)$")
PRIORITY_RE = re.compile(r"^P\d$")

# The UI's 12 domains are document categories; NDMO's are subject domains, and
# the two sets do not line up one-to-one. Domains with no NDMO counterpart
# (training, audit, risk, meetings) borrow the governance controls that actually
# govern those documents.
#
# 5_Data_Security has no NDMO controls at all: section 9.15 of the standards
# hands the Data Security and Protection domain to the National Cybersecurity
# Authority, so the PDF defines the domain but publishes no specifications for
# it. Classification and personal-data controls are the closest published
# requirements that security documents can actually be judged against.
DOMAIN_MAP: dict[str, list[str]] = {
    "1_Data_Governance": ["DG"],
    "2_Data_Catalog": ["MCM", "RMD"],
    "3_Data_Quality": ["DQ"],
    "4_Data_Operations": ["DO", "DAM"],
    "5_Data_Security": ["DC", "PDP"],
    "6_Personal_Data_Protection": ["PDP"],
    "7_Data_Classification": ["DC"],
    "8_Training_Awareness": ["DG"],
    "9_Audit_Compliance": ["DG", "FOI"],
    "10_Risk_Management": ["DG", "DO"],
    "11_Governance_Meetings": ["DG"],
    "12_Supporting_Documents": ["DSI", "DCM", "FOI", "DVR", "OD", "BIA"],
}

# The evaluator asks the model for a decision on every control of a domain in a
# single JSON reply. Past roughly this many, the reply runs long enough to get
# truncated, and file_eval_done then drops the whole file's result. NDMO ranks
# specifications P1-P3, so trimming takes the lowest priorities first rather
# than an arbitrary slice.
MAX_CONTROLS_PER_DOMAIN = 25


def parse_policies(pdf_path: Path) -> list[dict[str, Any]]:
    """Pull every specification row out of the standards PDF's tables."""
    controls: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    cells = [(c or "").strip() for c in row]
                    non_empty = [c for c in cells if c]
                    if not non_empty:
                        continue

                    head = non_empty[0]
                    m = SPEC_ID_RE.match(head)
                    if m:
                        rest = non_empty[1:]
                        priority = ""
                        if rest and PRIORITY_RE.match(rest[-1]):
                            priority = rest.pop()
                        name = rest[0] if rest else ""
                        body = " ".join(rest[1:]) if len(rest) > 1 else ""
                        current = {
                            "id": head,
                            "domain": m.group(1),
                            "name": name,
                            "body": body,
                            "priority": priority,
                        }
                        # A specification can repeat across pages; keep the
                        # first and let later rows append to it.
                        if head in by_id:
                            current = by_id[head]
                        else:
                            by_id[head] = current
                            controls.append(current)
                        continue

                    # Continuation row: the specification text wrapped onto the
                    # next line with an empty ID column.
                    if current is not None and not SPEC_ID_RE.match(head):
                        if PRIORITY_RE.match(head) or head.isdigit():
                            continue
                        if len(head) > 3:
                            current["body"] = (current["body"] + " " + " ".join(non_empty)).strip()

    return controls


def parse_oe(pdf_path: Path) -> list[dict[str, Any]]:
    """Pull the OE metrics out of the index PDF's labelled field blocks."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)

    # Each metric is a run of "Label  value" lines starting at "Metric ID".
    blocks = re.split(r"\n(?=Metric ID\s+[A-Z]{2,4}\.OE\.\d+)", text)
    metrics: list[dict[str, Any]] = []

    def field(block: str, label: str, stop: list[str]) -> str:
        stop_alt = "|".join(re.escape(s) for s in stop)
        m = re.search(
            rf"^{re.escape(label)}\s+(.*?)(?=\n(?:{stop_alt})\s|\Z)",
            block,
            re.S | re.M,
        )
        if not m:
            return ""
        return re.sub(r"\s*\n\s*", " ", m.group(1)).strip()

    labels = [
        "Metric ID",
        "Metric Name",
        "Metric Description",
        "Domain Name",
        "Data Platforms",
        "Definitions",
        "Calculation",
        "Measurement Unit",
        "Acceptable Threshold",
        "Scale Intervals",
        "Version History",
        "Dependencies",
        "Element Name",
    ]

    for block in blocks:
        mid = re.match(r"Metric ID\s+([A-Z]{2,4}\.OE\.\d+)", block)
        if not mid:
            continue
        cid = mid.group(1)
        dm = OE_ID_RE.match(cid)
        if not dm:
            continue
        metrics.append(
            {
                "id": cid,
                "domain": dm.group(1),
                "name": field(block, "Metric Name", labels),
                "body": field(block, "Metric Description", labels),
                "calculation": field(block, "Calculation", labels),
                "threshold": field(block, "Acceptable Threshold", labels),
                "scale": field(block, "Scale Intervals", labels),
                # Sorted ahead of P1. An OE metric carries a formula, a
                # threshold and a 0-5 scale, so it is the one kind of control
                # here that can be judged on evidence rather than prose, and
                # it should survive the per-domain trim.
                "priority": "P0",
            }
        )
    return metrics


def to_control(item: dict[str, Any]) -> dict[str, str]:
    """Shape a parsed row into the 5-field schema the evaluator expects."""
    name = item.get("name", "")
    body = item.get("body", "")
    description = f"{name}. {body}".strip(". ").strip() if name else body
    priority = item.get("priority", "")
    if priority:
        description = f"{description} (Priority: {priority})"
    return {
        "id": item["id"],
        "description": re.sub(r"\s+", " ", description).strip(),
        "calculation": re.sub(r"\s+", " ", item.get("calculation", "")).strip(),
        "threshold": re.sub(r"\s+", " ", item.get("threshold", "")).strip(),
        "scale": re.sub(r"\s+", " ", item.get("scale", "")).strip(),
    }


def main() -> int:
    for p in (POLICIES_PDF, OE_PDF):
        if not p.is_file():
            sys.exit(f"missing PDF: {p}")

    specs = parse_policies(POLICIES_PDF)
    metrics = parse_oe(OE_PDF)
    print(f"parsed {len(specs)} specifications and {len(metrics)} OE metrics")

    everything = specs + metrics
    by_domain: dict[str, list[dict[str, Any]]] = {}
    for item in everything:
        by_domain.setdefault(item["domain"], []).append(item)

    found = sorted(by_domain)
    print(f"NDMO domains present: {', '.join(found)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    empty: list[str] = []
    for ui_domain, prefixes in DOMAIN_MAP.items():
        items: list[dict[str, Any]] = []
        seen: set[str] = set()
        for prefix in prefixes:
            for item in by_domain.get(prefix, []):
                if item["id"] in seen:
                    continue
                seen.add(item["id"])
                items.append(item)
        # P1 first, then P2/P3, then OE metrics (which carry no priority).
        items.sort(key=lambda i: (i.get("priority") or "P9", i["id"]))
        controls = [to_control(i) for i in items]
        controls = [c for c in controls if c["id"] and c["description"]]
        if len(controls) > MAX_CONTROLS_PER_DOMAIN:
            dropped = len(controls) - MAX_CONTROLS_PER_DOMAIN
            controls = controls[:MAX_CONTROLS_PER_DOMAIN]
            print(f"  {ui_domain:28} trimmed {dropped} lower-priority controls")
        if not controls:
            empty.append(ui_domain)
        payload = {"framework_name": "NDI", "controls": controls}
        out = OUT_DIR / f"{ui_domain}.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        total += len(controls)
        print(f"  {ui_domain:28} {len(controls):3} controls -> {out.name}")

    print(f"\nwrote {len(DOMAIN_MAP)} files, {total} control entries, into {OUT_DIR}")
    if empty:
        print(f"WARNING: these domains got no controls and will evaluate against nothing: {empty}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
