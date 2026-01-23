"""
Utilities Module
Handles saving and loading of framework data (JSON controls and evaluation prompts)
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional
from datetime import datetime


def save_framework_data(
    framework_name: str, 
    controls_json: Dict[str, Any], 
    evaluation_prompt: str,
    metadata: Dict[str, Any] = None
) -> None:
    """
    Save framework controls JSON and evaluation prompt to config/frameworks/{framework_name}/
    
    Creates directory structure if it doesn't exist.
    Saves:
    - controls.json: The extracted controls JSON
    - evaluation_prompt.txt: The generated evaluation prompt
    - framework_metadata.json: Metadata about sections, validation, etc. (if provided)
    
    Args:
        framework_name: Name of the framework (used for directory name)
        controls_json: Dictionary containing controls, metadata, and filters
        evaluation_prompt: Generated evaluation prompt string
        metadata: Optional dictionary containing framework metadata:
            - sections: list of section names
            - total_size: total character count
            - extracted_at: timestamp
            - keywords_found: dictionary of keywords per section
            - validation_status: validation results
    """
    # Get project root (services/ai-service/)
    project_root = Path(__file__).parent.parent.parent
    base_dir = project_root / "config" / "frameworks"
    framework_dir = base_dir / framework_name
    framework_dir.mkdir(parents=True, exist_ok=True)
    
    # Save controls JSON
    controls_path = framework_dir / "controls.json"
    with open(controls_path, "w", encoding="utf-8") as f:
        json.dump(controls_json, f, indent=2, ensure_ascii=False)
    
    # Save evaluation prompt
    prompt_path = framework_dir / "evaluation_prompt.txt"
    with open(prompt_path, "w", encoding="utf-8") as f:
        f.write(evaluation_prompt)
    
    # Save metadata if provided
    if metadata:
        from datetime import datetime
        # Add timestamp if not present
        if 'extracted_at' not in metadata:
            metadata['extracted_at'] = datetime.now().isoformat()
        
        metadata_path = framework_dir / "framework_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)


def load_framework_data(framework_name: str) -> Tuple[Dict[str, Any], str]:
    """
    Load saved framework controls JSON and evaluation prompt.
    
    Args:
        framework_name: Name of the framework to load
        
    Returns:
        Tuple of (controls_json, evaluation_prompt)
        
    Raises:
        FileNotFoundError: If framework data doesn't exist
    """
    # Get project root (services/ai-service/)
    project_root = Path(__file__).parent.parent.parent
    framework_dir = project_root / "config" / "frameworks" / framework_name
    
    # Load controls JSON
    controls_path = framework_dir / "controls.json"
    if not controls_path.exists():
        raise FileNotFoundError(f"Controls JSON not found: {controls_path}")
    
    with open(controls_path, "r", encoding="utf-8") as f:
        controls_json = json.load(f)
    
    # Load evaluation prompt
    prompt_path = framework_dir / "evaluation_prompt.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Evaluation prompt not found: {prompt_path}")
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        evaluation_prompt = f.read()
    
    return controls_json, evaluation_prompt


def list_saved_frameworks() -> List[str]:
    """
    List all saved frameworks in config/frameworks/
    
    Returns:
        List of framework names
    """
    # Get project root (services/ai-service/)
    project_root = Path(__file__).parent.parent.parent
    frameworks_dir = project_root / "config" / "frameworks"
    
    if not frameworks_dir.exists():
        return []
    
    frameworks = [
        d.name for d in frameworks_dir.iterdir() 
        if d.is_dir() and (d / "controls.json").exists() and (d / "evaluation_prompt.txt").exists()
    ]
    return sorted(frameworks)


def save_evaluation_report(
    evaluation_report: Dict[str, Any],
    framework_name: str,
    applicant_name: Optional[str] = None
) -> Path:
    """
    Save evaluation report to data/outputs/evaluations/
    
    Args:
        evaluation_report: Dictionary containing evaluation results
        framework_name: Name of the framework used for evaluation
        applicant_name: Optional name/identifier for the applicant
        
    Returns:
        Path to the saved evaluation report file
    """
    # Get project root (services/ai-service/)
    project_root = Path(__file__).parent.parent.parent
    outputs_dir = project_root / "data" / "outputs" / "evaluations"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if applicant_name:
        # Sanitize applicant name for filename
        safe_name = "".join(c for c in applicant_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{framework_name}_{safe_name}_{timestamp}.json"
    else:
        filename = f"{framework_name}_evaluation_{timestamp}.json"
    
    report_path = outputs_dir / filename
    
    # Save evaluation report
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(evaluation_report, f, indent=2, ensure_ascii=False)
    
    return report_path


def get_input_paths() -> Dict[str, Path]:
    """
    Get standard input directory paths.
    
    Returns:
        Dictionary with paths:
        - frameworks: Path to framework PDFs directory
        - applicants: Path to applicant PDFs directory
        - vector_db: Path to vector DB input PDFs directory
    """
    project_root = Path(__file__).parent.parent.parent
    return {
        "frameworks": project_root / "data" / "inputs" / "frameworks",
        "applicants": project_root / "data" / "inputs" / "applicants",
        "vector_db": project_root / "data" / "inputs" / "vector_db"
    }
