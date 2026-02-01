"""
Evaluation service: submit 15 files + framework, run agent, return mimic JSON + report path.
No DB; files and report saved to filesystem.
"""

from typing import Any

from src.agent import run_evaluation_agent


class EvaluationService:
    """Orchestrates evaluation submission and agent run."""

    def submit_evaluation(
        self,
        framework_name: str,
        files: list[tuple[str, bytes]],
        control_ids_per_file: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Submit an evaluation: files (1+) + framework name. control_ids_per_file must have the same
        length as files (one comma-separated control ID string per file).
        Runs the LangGraph agent, saves report PDF to data/reports/{evaluation_id}.pdf.
        Returns mimic_json, evaluation_id, report_path, file_evaluations.
        """
        return run_evaluation_agent(
            framework_name=framework_name,
            files=files,
            control_ids_per_file=control_ids_per_file,
        )
