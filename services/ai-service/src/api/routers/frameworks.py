"""Framework endpoints: setup, list (future)."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.api.models import ControlSummary, SetupFrameworkResponse
from src.services import FrameworkService

router = APIRouter(prefix="/api/v1/frameworks", tags=["frameworks"])


@router.post("/setup", response_model=SetupFrameworkResponse)
async def setup_framework(
    framework_name: str = Form(..., min_length=1, description="Framework identifier"),
    section_names: str = Form(
        ...,
        description="Comma-separated section names (one per PDF, same order as files). Example: policies,procedures,controls",
    ),
    files: list[UploadFile] = File(..., description="PDF files (same order as section_names)"),
) -> SetupFrameworkResponse:
    """
    Initialize a framework by extracting controls from multiple uploaded PDF sections.
    
    Section names must be provided as a single comma-separated string with one name per file, in the same order as the uploaded files.
    
    Parameters:
        framework_name: Framework identifier.
        section_names: Comma-separated section names (one name per PDF, same order as `files`).
        files: Uploaded PDF files corresponding to `section_names`.
    
    Returns:
        SetupFrameworkResponse: Summary of the created framework, including `framework_name`, `total_controls`, `sections`, and `created_at`.
    
    Raises:
        HTTPException: Status 400 for input validation errors (mismatched counts between section names and files, empty or non-PDF uploads, empty file bodies, or empty section names).
    """
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
    for name, upload in zip(section_names_list, files):
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
        pdf_sections.append((name.strip(), body))

    service = FrameworkService()
    result = service.setup_framework(framework_name=framework_name, pdf_sections=pdf_sections)

    return SetupFrameworkResponse(
        framework_name=result["framework_name"],
        total_controls=result["total_controls"],
        sections=[ControlSummary(**s) for s in result["sections"]],
        created_at=result["created_at"],
    )