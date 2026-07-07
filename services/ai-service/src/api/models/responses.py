"""Response schemas for API endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Structured error response for API exceptions."""

    error: str = Field(..., description="Error code or type")
    message: str = Field(..., description="Human-readable message")
    detail: Optional[str] = Field(None, description="Additional detail (e.g. framework_name)")


class ControlSummary(BaseModel):
    """Summary of extracted controls for one section (PDF)."""

    section_name: str = Field(..., description="Name of the section (PDF)")
    controls_count: int = Field(..., ge=0, description="Number of controls extracted")
    json_path: str = Field(..., description="Relative path to the saved JSON file")


class SetupFrameworkResponse(BaseModel):
    """Response after successfully setting up a framework from multiple PDFs."""

    framework_name: str = Field(..., description="Framework identifier")
    total_controls: int = Field(..., ge=0, description="Total controls across all sections")
    sections: list[ControlSummary] = Field(default_factory=list, description="Per-section summary")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the setup completed")


class SubmitEvaluationResponse(BaseModel):
    """Response after submitting an evaluation (files + framework)."""

    evaluation_id: str = Field(..., description="Unique evaluation run ID")
    mimic_json: dict = Field(..., description="framework_name -> field_N -> comma-separated control IDs assigned to that file")
    report_path: str = Field("", description="Path to the generated report PDF")
    file_evaluations: list[dict] = Field(default_factory=list, description="Per-file assessment results")


class ExtractionError(Exception):
    """Raised when framework extraction fails (e.g. LLM API error)."""

    def __init__(self, message: str, framework_name: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.framework_name = framework_name
