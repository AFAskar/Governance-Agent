"""
Evaluation endpoints: submit files + framework, download the report PDF.
Supports domain_ids parameter to specify which domain each file belongs to.
"""

import os
import re
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from starlette.concurrency import run_in_threadpool

from src.api.models import SubmitEvaluationResponse
from src.services import EvaluationService

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])

_REPORTS_DIR = Path(__file__).resolve().parents[3] / "data" / "reports"

_MAX_FILES = 120  # 12 domains × 10 files per domain
_MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024
_FRAMEWORK_NAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")
_DOMAIN_IDS_RE = re.compile(r"^[a-zA-Z0-9_,\-\s]+$")


def _sanitize_filename(filename: str) -> str:
    """Strip path components and restrict to safe characters."""
    name = Path(filename).name
    name = re.sub(r"[^a-zA-Z0-9._\-]", "_", name)
    name = name.lstrip(".")
    return (name or "file")[:255]


@router.post("/submit", response_model=SubmitEvaluationResponse)
async def submit_evaluation(
    framework_name: str = Form(
        ..., min_length=1, max_length=64, description="Framework identifier (e.g. NDI)"
    ),
    files: list[UploadFile] = File(
        ..., description="Files (PDF, DOCX, PPTX, CSV, XLSX); 1 or more"
    ),
    domain_ids: str = Form(
        default="",
        description="Comma-separated domain IDs, one per file (e.g. '1_Data_Governance,1_Data_Governance,2_Data_Catalog')",
    ),
) -> SubmitEvaluationResponse:
    """
    Submit an evaluation: files + framework name + domain_ids.
    domain_ids is a comma-separated list of domain IDs (one per file).
    Files are evaluated against the controls for their respective domains.
    Returns DB-mimic JSON + evaluation_id + report_path.
    """
    if not _FRAMEWORK_NAME_RE.match(framework_name):
        raise HTTPException(
            status_code=400,
            detail="framework_name must contain only letters, digits, underscores, or hyphens",
        )

    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    n_files = len(files)
    if n_files > _MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {_MAX_FILES} files allowed")

    # Parse domain_ids
    domain_ids_list = []
    if domain_ids.strip():
        if not _DOMAIN_IDS_RE.match(domain_ids):
            raise HTTPException(status_code=400, detail="Invalid domain_ids format")
        domain_ids_list = [d.strip() for d in domain_ids.split(",")]
        if len(domain_ids_list) != n_files:
            raise HTTPException(
                status_code=400,
                detail=f"domain_ids has {len(domain_ids_list)} entries but {n_files} files; they must match",
            )

    file_tuples: list[tuple[str, bytes]] = []
    for u in files:
        if not u.filename:
            raise HTTPException(status_code=400, detail="Each file must have a filename")
        body = await u.read()
        if not body:
            raise HTTPException(status_code=400, detail=f"File '{u.filename}' is empty")
        if len(body) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File '{u.filename}' exceeds {_MAX_UPLOAD_BYTES // (1024 * 1024)}MB limit",
            )
        file_tuples.append((_sanitize_filename(u.filename), body))

    # The agent run is CPU/IO-heavy and can take minutes; run it in the
    # threadpool so the event loop keeps serving health checks and other requests.
    service = EvaluationService()
    result = await run_in_threadpool(
        service.submit_evaluation,
        framework_name=framework_name,
        files=file_tuples,
        domain_ids=domain_ids_list if domain_ids_list else None,
    )

    return SubmitEvaluationResponse(
        evaluation_id=result["evaluation_id"],
        mimic_json=result["mimic_json"],
        report_path=result.get("report_path", ""),
        file_evaluations=result.get("file_evaluations", []),
    )


@router.get("/{evaluation_id}/report")
async def get_evaluation_report(evaluation_id: str) -> FileResponse:
    """Download the generated report PDF for an evaluation."""
    try:
        uuid.UUID(evaluation_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="evaluation_id must be a valid UUID") from exc

    path = _REPORTS_DIR / f"{evaluation_id}.pdf"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"evaluation_report_{evaluation_id}.pdf",
    )
