"""
Framework service: orchestrates framework setup (extraction + save).
Used by API and CLI.
"""

import logging
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from src.core import extract_controls_from_pdfs
from src.rag import index_framework
from src.utils import get_input_paths, save_extraction_json


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


class FrameworkService:
    """Orchestrates framework setup operations."""

    def setup_framework(
        self,
        framework_name: str,
        pdf_sections: list[tuple[str, bytes]],
    ) -> dict[str, Any]:
        """
        Process multiple PDFs with section names: extract controls, save JSON per section, and index into vector DB.

        Steps:
        1. Save uploaded PDFs to a temp directory with section names as filenames.
        2. Extract controls from each PDF in parallel (existing core logic).
        3. Save one JSON per section under config/frameworks/{framework_name}/{section_name}.json.
        4. Persist PDFs to data/inputs/vector_db/{framework_name}/ and call index_framework to populate vector DB.
        5. Return summary (framework_name, total_controls, sections, created_at).

        Args:
            framework_name: Framework identifier.
            pdf_sections: List of (section_name, pdf_bytes). Section name is used as the JSON filename.

        Returns:
            Dict with keys: framework_name, total_controls, sections (list of {section_name, controls_count, json_path}), created_at.
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
