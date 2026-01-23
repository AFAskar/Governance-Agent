"""
Main entry point for the Compliance Framework Evaluation System.

This demonstrates the complete pipeline:
1. Framework Setup: Extract controls from framework PDF
2. Document Processing: Process and index framework documents
3. Evaluation: Evaluate applicant documents against framework
"""

from pathlib import Path
import glob
from src.core import (
    extract_controls_from_framework, 
    evaluate_applicant,
    organize_pdfs_by_section,
    validate_framework_sections,
    extract_controls_from_sections,
    create_master_prompt
)
from src.processing import extract_text_from_pdf, chunk_text
from src.prompts import generate_evaluation_prompt
from src.utils import (
    save_framework_data, 
    load_framework_data, 
    list_saved_frameworks,
    save_evaluation_report,
    get_input_paths
)
#   from src.embeddings import (
#    GemmaEmbedder, initialize_qdrant, add_documents, search_similar
#)


def setup_framework(pdf_paths: str | list[str], framework_name: str):
    """
    Setup a new compliance framework from PDF(s).
    
    Supports single file, list of files, or directory path.
    For multiple PDFs, organizes them into sections, validates, extracts controls,
    and creates a master evaluation prompt.
    
    Pipeline:
    1. Normalize input to list of PDF paths
    2. Organize PDFs into sections (using LLM content analysis)
    3. Validate framework sections
    4. Extract controls from each section
    5. Create master evaluation prompt
    6. Save framework data with metadata
    
    Args:
        pdf_paths: Single file path (str), list of file paths, or directory path
        framework_name: Name of the framework
        
    Returns:
        Tuple of (consolidated_controls_json, master_evaluation_prompt, metadata)
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
    
    # For single PDF, use original workflow for backward compatibility
    if len(pdf_paths_list) == 1:
        pdf_text = extract_text_from_pdf(pdf_paths_list[0])
        controls_json = extract_controls_from_framework(pdf_text, framework_name)
        evaluation_prompt = generate_evaluation_prompt(controls_json, framework_name)
        save_framework_data(framework_name, controls_json, evaluation_prompt)
        return controls_json, evaluation_prompt
    
    # Multi-PDF workflow
    # 1. Organize PDFs into sections
    organized_sections = organize_pdfs_by_section(pdf_paths_list, framework_name)
    
    # 2. Validate framework sections
    validation_result = validate_framework_sections(organized_sections, framework_name)
    
    # 3. Extract controls from each section
    section_controls = extract_controls_from_sections(organized_sections, framework_name)
    
    # 4. Create master evaluation prompt
    master_prompt = create_master_prompt(section_controls, organized_sections, framework_name)
    
    # 5. Consolidate controls JSON (combine all sections)
    consolidated_controls = {
        "framework_name": framework_name,
        "sections": list(organized_sections.keys()),
        "controls": [],
        "metadata": {
            "total_sections": len(organized_sections),
            "extraction_method": "multi_pdf_consolidated"
        },
        "filters": {}
    }
    
    # Combine controls from all sections
    all_categories = set()
    for section_name, controls in section_controls.items():
        if not controls.get('incomplete'):
            if 'controls' in controls:
                for control in controls['controls']:
                    control['section'] = section_name
                    consolidated_controls['controls'].append(control)
                    if 'category' in control:
                        all_categories.add(control['category'])
    
    consolidated_controls['filters']['categories'] = list(all_categories)
    consolidated_controls['metadata']['total_controls'] = len(consolidated_controls['controls'])
    
    # 6. Prepare metadata
    from datetime import datetime
    metadata = {
        "sections": list(organized_sections.keys()),
        "total_size": validation_result.get('total_size', 0),
        "extracted_at": datetime.now().isoformat(),
        "keywords_found": validation_result.get('keywords_found', {}),
        "validation_status": validation_result.get('status', 'pass'),
        "validation_checks": validation_result.get('checks', {}),
        "section_paths": organized_sections
    }
    
    # 7. Save framework data
    save_framework_data(framework_name, consolidated_controls, master_prompt, metadata)
    
    return consolidated_controls, master_prompt, metadata


def index_framework_documents(
    pdf_paths: str | list[str], 
    framework_name: str
):
    """
    Index framework documents in vector database.
    
    Supports single file, list of files, or directory path.
    Each PDF is processed individually: extract text, chunk, then all chunks are embedded together.
    
    Pipeline:
    1. For each PDF:
       - Extract text from PDF
       - Chunk text
    2. Generate embeddings for all chunks
    3. Store in Qdrant
    
    Args:
        pdf_paths: Single file path (str), list of file paths, or directory path
        framework_name: Name of the framework
        
    Returns:
        Tuple of (qdrant_client, collection_name, embedder)
    """
    # Lazy import - only load heavy ML libraries when this function is called
    from src.embeddings import (
        GemmaEmbedder, initialize_qdrant, add_documents
    )
    
    # Normalize input to list of PDF paths
    if isinstance(pdf_paths, list):
        pdf_paths_list = pdf_paths
    else:
        pdf_path = Path(pdf_paths)
        if pdf_path.is_dir():
            pdf_paths_list = sorted(glob.glob(f"{pdf_paths}/*.pdf"))
        else:
            pdf_paths_list = [pdf_paths]
    
    # Process each PDF individually: extract text, then chunk
    all_chunks = []
    for pdf_path in pdf_paths_list:
        # Extract text from this PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        
        # Chunk this PDF's text
        pdf_chunks = chunk_text(pdf_text, framework_name=framework_name)
        
        # Add source PDF metadata to each chunk
        pdf_name = Path(pdf_path).name
        for chunk in pdf_chunks:
            chunk["metadata"]["source_pdf"] = pdf_name
            chunk["metadata"]["source_path"] = str(pdf_path)
        
        all_chunks.extend(pdf_chunks)
    
    if not all_chunks:
        raise ValueError("No chunks could be created from the provided PDFs")
    
    # Initialize embedder and generate embeddings for all chunks
    embedder = GemmaEmbedder()
    embedding_dim = embedder.get_embedding_dim()
    
    chunk_texts = [chunk["text"] for chunk in all_chunks]
    embeddings = embedder.embed_batch(chunk_texts)
    
    collection_name = f"{framework_name}_chunks"
    qdrant_client = initialize_qdrant(collection_name, embedding_dim)
    add_documents(qdrant_client, collection_name, all_chunks, embeddings)
    
    return qdrant_client, collection_name, embedder


def evaluate_applicant_documents(
    applicant_pdf_paths: list[str],
    framework_name: str,
    applicant_name: str = None,
    save_report: bool = True
):
    """
    Evaluate applicant documents against a framework.
    
    Pipeline:
    1. Load framework data
    2. Extract text from applicant PDFs
    3. Evaluate using LLM
    4. Save evaluation report (optional)
    
    Args:
        applicant_pdf_paths: List of paths to applicant PDF files
        framework_name: Name of the framework to evaluate against
        applicant_name: Optional name/identifier for the applicant
        save_report: Whether to save the evaluation report to disk
    """
    controls_json, evaluation_prompt = load_framework_data(framework_name)
    
    applicant_docs = []
    for pdf_path in applicant_pdf_paths:
        doc_text = extract_text_from_pdf(pdf_path)
        applicant_docs.append(doc_text)
    
    evaluation_report = evaluate_applicant(
        applicant_docs, evaluation_prompt, controls_json
    )
    
    if save_report:
        save_evaluation_report(
            evaluation_report, 
            framework_name, 
            applicant_name
        )
    
    return evaluation_report


def main():
    """Main entry point demonstrating the pipeline."""
    print("\n" + "="*60)
    print("Compliance Framework Evaluation System")
    print("="*60)
    
    # Show directory structure
    paths = get_input_paths()
    print("\n📁 Directory Structure:")
    print(f"  Input PDFs (Frameworks): {paths['frameworks']}")
    print(f"  Input PDFs (Applicants): {paths['applicants']}")
    print(f"  Input PDFs (Vector DB): {paths['vector_db']}")
    print(f"  Framework Outputs: config/frameworks/")
    print(f"  Evaluation Reports: data/outputs/evaluations/")
    print(f"  Vector Database: config/vector_db/")
    
    # Example usage (commented out - user should provide actual paths)
    print("\n📝 Example pipeline usage:")
    print("\n1. Setup a framework:")
    print("   Place framework PDF in: data/inputs/frameworks/")
    print("   setup_framework('data/inputs/frameworks/my_framework.pdf', 'my_framework')")
    
    print("\n2. Index framework documents (supports single file, list, or directory):")
    print("   # Single file:")
    print("   index_framework_documents('data/inputs/frameworks/my_framework.pdf', 'my_framework')")
    print("   # Directory (all PDFs in directory):")
    print("   index_framework_documents('data/inputs/vector_db/my_framework/', 'my_framework')")
    print("   # List of files:")
    print("   index_framework_documents(['file1.pdf', 'file2.pdf'], 'my_framework')")
    
    print("\n3. Evaluate applicant documents:")
    print("   Place applicant PDFs in: data/inputs/applicants/")
    print("   evaluate_applicant_documents(")
    print("       ['data/inputs/applicants/applicant1.pdf'],")
    print("       'my_framework',")
    print("       applicant_name='applicant1'")
    print("   )")
    
    print("\n" + "="*60)
    print("Pipeline ready! Place your PDFs in the directories above and run the functions.")
    print("="*60 + "\n")



def test_paths():
    paths = get_input_paths()

    print(f"  Input PDFs (Frameworks): {paths['frameworks']}")
    print(f"  Input PDFs (Applicants): {paths['applicants']}")

if __name__ == "__main__":
    #main()
    test_paths()
    vector_db_path = "data/inputs/vector_db"
    framework_name = "NDI"
    #index_framework_documents(vector_db_path, framework_name)
    framework_path = "data/inputs/frameworks/"
    setup_framework(framework_path, framework_name)

    
