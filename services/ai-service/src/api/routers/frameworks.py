"""Framework endpoints: setup, list (future)."""

import os
import re

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from src.api.models import ControlSummary, SetupFrameworkResponse
from src.services import FrameworkService

router = APIRouter(prefix="/api/v1/frameworks", tags=["frameworks"])

_MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50")) * 1024 * 1024
_FRAMEWORK_NAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


@router.post("/setup", response_model=SetupFrameworkResponse)
async def setup_framework(
    framework_name: str = Form(
        ..., min_length=1, max_length=64, description="Framework identifier"
    ),
    section_names: str = Form(
        ...,
        description="Comma-separated section names (one per PDF, same order as files). Example: policies,procedures,controls",
    ),
    files: list[UploadFile] = File(..., description="PDF files (same order as section_names)"),
) -> SetupFrameworkResponse:
    """
    Setup a new framework by extracting controls from multiple PDFs.
    Each PDF has a section name; controls are saved as config/frameworks/{framework_name}/{section_name}.json.
    Send section_names as one string: comma-separated names, one per file, in the same order as files.
    """
    if not _FRAMEWORK_NAME_RE.match(framework_name):
        raise HTTPException(
            status_code=400,
            detail="framework_name must contain only letters, digits, underscores, or hyphens",
        )

    section_names_list = [s.strip() for s in section_names.split(",") if s.strip()]
    if len(section_names_list) != len(files):
        raise HTTPException(
            status_code=400,
            detail=f"section_names ({len(section_names_list)} after splitting by comma) and files ({len(files)}) must have the same length. Use comma-separated names, e.g. name1,name2,name3",
        )
    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF file is required")

    # Validate PDFs and read bytes
    pdf_sections: list[tuple[str, bytes]] = []
    for name, upload in zip(section_names_list, files, strict=True):
        if not name or not name.strip():
            raise HTTPException(
                status_code=400,
                detail="Section names cannot be empty",
            )
        if not (upload.filename and upload.filename.lower().endswith(".pdf")):
            raise HTTPException(
                status_code=400,
                detail=f"File for section '{name}' must be a PDF (filename ending in .pdf)",
            )
        body = await upload.read()
        if not body:
            raise HTTPException(
                status_code=400,
                detail=f"File for section '{name}' is empty",
            )
        if len(body) > _MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File for section '{name}' exceeds {_MAX_UPLOAD_BYTES // (1024 * 1024)}MB limit",
            )
        pdf_sections.append((name.strip(), body))

    # Extraction fans out one LLM call per PDF; keep it off the event loop.
    service = FrameworkService()
    result = await run_in_threadpool(
        service.setup_framework, framework_name=framework_name, pdf_sections=pdf_sections
    )

    return SetupFrameworkResponse(
        framework_name=result["framework_name"],
        total_controls=result["total_controls"],
        sections=[ControlSummary(**s) for s in result["sections"]],
        created_at=result["created_at"],
    )
