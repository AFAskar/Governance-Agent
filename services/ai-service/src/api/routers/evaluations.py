"""
Evaluation endpoints: submit files + framework, get mimic JSON + report PDF path.
Number of files is flexible; one control_ids field per file (control_ids_1, control_ids_2, ...).
"""

import os
import re
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.api.models import SubmitEvaluationResponse
from src.services import EvaluationService

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])

_MAX_FILES = 50
_MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024
_FRAMEWORK_NAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")
_CONTROL_IDS_RE = re.compile(r"^[a-zA-Z0-9.,\-_\s]*$")


def _sanitize_filename(filename: str) -> str:
    """Strip path components and restrict to safe characters."""
    name = Path(filename).name
    name = re.sub(r"[^a-zA-Z0-9._\-]", "_", name)
    name = name.lstrip(".")
    return (name or "file")[:255]


def _control_ids_form(i: int, default: str = ""):
    return Form(
        default=default, description=f"Comma-separated control IDs for file {i}"
    )


@router.post("/submit", response_model=SubmitEvaluationResponse)
async def submit_evaluation(
    framework_name: str = Form(
        ..., min_length=1, max_length=64, description="Framework identifier (e.g. NDI)"
    ),
    files: list[UploadFile] = File(
        ..., description="Files (PDF, DOCX, PPTX, CSV, XLSX); 1 or more"
    ),
    control_ids_1: str = _control_ids_form(1),
    control_ids_2: str = _control_ids_form(2),
    control_ids_3: str = _control_ids_form(3),
    control_ids_4: str = _control_ids_form(4),
    control_ids_5: str = _control_ids_form(5),
    control_ids_6: str = _control_ids_form(6),
    control_ids_7: str = _control_ids_form(7),
    control_ids_8: str = _control_ids_form(8),
    control_ids_9: str = _control_ids_form(9),
    control_ids_10: str = _control_ids_form(10),
    control_ids_11: str = _control_ids_form(11),
    control_ids_12: str = _control_ids_form(12),
    control_ids_13: str = _control_ids_form(13),
    control_ids_14: str = _control_ids_form(14),
    control_ids_15: str = _control_ids_form(15),
    control_ids_16: str = _control_ids_form(16),
    control_ids_17: str = _control_ids_form(17),
    control_ids_18: str = _control_ids_form(18),
    control_ids_19: str = _control_ids_form(19),
    control_ids_20: str = _control_ids_form(20),
) -> SubmitEvaluationResponse:
    """
    Submit an evaluation: files + framework name. Each file has its own control_ids field
    (control_ids_1 for file 1, control_ids_2 for file 2, etc.). Each value = comma-separated IDs.
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
        raise HTTPException(
            status_code=400, detail=f"Maximum {_MAX_FILES} files allowed"
        )

    control_ids_fields = [
        control_ids_1,
        control_ids_2,
        control_ids_3,
        control_ids_4,
        control_ids_5,
        control_ids_6,
        control_ids_7,
        control_ids_8,
        control_ids_9,
        control_ids_10,
        control_ids_11,
        control_ids_12,
        control_ids_13,
        control_ids_14,
        control_ids_15,
        control_ids_16,
        control_ids_17,
        control_ids_18,
        control_ids_19,
        control_ids_20,
    ]
    control_ids_per_file = []
    for s in control_ids_fields[:n_files]:
        ids = s.strip()
        if ids and not _CONTROL_IDS_RE.match(ids):
            raise HTTPException(
                status_code=400, detail=f"Invalid control ID format: {ids[:100]}"
            )
        control_ids_per_file.append(ids)

    file_tuples: list[tuple[str, bytes]] = []
    for u in files:
        if not u.filename:
            raise HTTPException(
                status_code=400, detail="Each file must have a filename"
            )
        body = await u.read()
        if not body:
            raise HTTPException(status_code=400, detail=f"File '{u.filename}' is empty")
        if len(body) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File '{u.filename}' exceeds {_MAX_UPLOAD_BYTES // (1024 * 1024)}MB limit",
            )
        file_tuples.append((_sanitize_filename(u.filename), body))

    service = EvaluationService()
    result = service.submit_evaluation(
        framework_name=framework_name,
        files=file_tuples,
        control_ids_per_file=control_ids_per_file,
    )

    return SubmitEvaluationResponse(
        evaluation_id=result["evaluation_id"],
        mimic_json=result["mimic_json"],
        report_path=result.get("report_path", ""),
        file_evaluations=result.get("file_evaluations", []),
    )
