"""
Framework service: orchestrates framework setup (extraction + save).
Used by API and CLI.
"""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from src.core import extract_controls_from_pdfs
from src.rag import index_framework
from src.utils import get_input_paths, save_extraction_json


def _project_root() -> Path:
    """
    Get the repository's project root directory.
    
    Resolves this file's location and returns the Path three levels above it.
    
    Returns:
        Path: Path object pointing to the repository root directory.
    """
    return Path(__file__).resolve().parent.parent.parent


class FrameworkService:
    """Orchestrates framework setup operations."""

    def setup_framework(
        self,
        framework_name: str,
        pdf_sections: list[tuple[str, bytes]],
    ) -> dict[str, Any]:
        """
        Orchestrates extraction of controls from labeled PDF sections, saves per-section JSON, indexes PDFs into the vector DB, and returns a summary.
        
        Parameters:
            framework_name (str): Identifier used for saved files and vector DB organization.
            pdf_sections (list[tuple[str, bytes]]): List of (section_name, pdf_bytes); each section_name is used as the JSON and PDF filename.
        
        Returns:
            dict: Summary containing:
                - framework_name: the provided framework_name.
                - total_controls: total number of extracted controls across all sections.
                - sections: list of objects with keys `section_name`, `controls_count`, and `json_path`.
                - created_at: UTC timestamp when the summary was created.
        """
        if not pdf_sections:
            raise ValueError("At least one PDF section is required")

        temp_dir = Path(tempfile.mkdtemp())
        try:
            pdf_paths_list: list[str] = []
            section_names_order: list[str] = []
            for section_name, content in pdf_sections:
                safe_name = Path(section_name).name or "section"
                path = temp_dir / f"{safe_name}.pdf"
                path.write_bytes(content)
                pdf_paths_list.append(str(path))
                section_names_order.append(safe_name)

            controls_arrays = extract_controls_from_pdfs(pdf_paths_list, framework_name)

            project_root = _project_root()
            sections_out: list[dict[str, Any]] = []
            total_controls = 0

            for section_name, controls_array in zip(section_names_order, controls_arrays):
                obj: dict[str, Any] = {"framework_name": framework_name, "controls": controls_array}
                pdf_path = str(temp_dir / f"{section_name}.pdf")
                saved_path = save_extraction_json(
                    framework_name, pdf_path, obj, custom_name=section_name
                )
                try:
                    json_path_rel = saved_path.relative_to(project_root)
                except ValueError:
                    json_path_rel = saved_path
                sections_out.append({
                    "section_name": section_name,
                    "controls_count": len(controls_array),
                    "json_path": str(json_path_rel),
                })
                total_controls += len(controls_array)

            # Persist PDFs for RAG and index into vector DB
            paths = get_input_paths()
            vector_db_dir = paths["vector_db"] / framework_name
            vector_db_dir.mkdir(parents=True, exist_ok=True)
            pdf_paths_for_rag: list[str] = []
            for (section_name, content), safe_name in zip(pdf_sections, section_names_order):
                out_pdf = vector_db_dir / f"{safe_name}.pdf"
                out_pdf.write_bytes(content)
                pdf_paths_for_rag.append(str(out_pdf))
            index_framework(framework_name, pdf_paths=pdf_paths_for_rag)

            return {
                "framework_name": framework_name,
                "total_controls": total_controls,
                "sections": sections_out,
                "created_at": datetime.utcnow(),
            }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)