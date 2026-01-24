"""
Main entry point for the Compliance Framework Evaluation System.
Simple flow: Extract controls → Compose → Generate prompt
"""

from pathlib import Path
import glob
from src.core.framework_extractor import extract_controls_from_framework
from src.core.framework_consolidator import extract_controls_from_pdfs, compose_master_framework
from src.processing import extract_text_from_pdf
from src.prompts import generate_evaluation_prompt
from src.utils import save_framework_data, get_input_paths


def setup_framework(pdf_paths: str | list[str], framework_name: str):
    """
    Setup a compliance framework from PDF(s).
    Simple flow: Extract controls → Compose → Generate prompt
    
    Args:
        pdf_paths: Single file path, list of files, or directory path
        framework_name: Name of the framework
        
    Returns:
        Tuple of (controls_json, evaluation_prompt)
    """
    # Normalize input to list of PDF paths
    if isinstance(pdf_paths, list):
        pdf_paths_list = pdf_paths
    else:
        pdf_path = Path(pdf_paths)
        if pdf_path.is_dir():
            pdf_paths_list = sorted(glob.glob(f"{pdf_paths}/*.pdf"))
        else:
            pdf_paths_list = [pdf_paths]
    
    if not pdf_paths_list:
        raise ValueError(f"No PDF files found: {pdf_paths}")
    
    # Single PDF - simple flow
    if len(pdf_paths_list) == 1:
        pdf_text = extract_text_from_pdf(pdf_paths_list[0])
        controls_json = extract_controls_from_framework(pdf_text, framework_name)
        evaluation_prompt = generate_evaluation_prompt(controls_json, framework_name)
        save_framework_data(framework_name, controls_json, evaluation_prompt)
        return controls_json, evaluation_prompt
    
    # Multiple PDFs - extract, compose, generate
    controls_arrays = extract_controls_from_pdfs(pdf_paths_list, framework_name)
    
    # Filter out empty arrays
    json_list = [arr for arr in controls_arrays if arr]
    
    # Compose into master framework
    if json_list:
        master_framework = compose_master_framework(json_list, framework_name)
    else:
        master_framework = {"framework_name": framework_name, "controls": []}
    
    # Generate prompt
    evaluation_prompt = generate_evaluation_prompt(master_framework, framework_name)
    
    # Save
    save_framework_data(framework_name, master_framework, evaluation_prompt)
    
    return master_framework, evaluation_prompt


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("Compliance Framework Evaluation System")
    print("="*60)
    
    paths = get_input_paths()
    print("\n📁 Directory Structure:")
    print(f"  Input PDFs (Frameworks): {paths['frameworks']}")
    print(f"  Input PDFs (Applicants): {paths['applicants']}")
    print(f"  Framework Outputs: config/frameworks/")
    
    print("\n📝 Usage:")
    print("   setup_framework('data/inputs/frameworks/', 'framework_name')")
    print("="*60 + "\n")


if __name__ == "__main__":
    framework_path = "data/inputs/frameworks/"
    framework_name = "NDI"
    setup_framework(framework_path, framework_name)
