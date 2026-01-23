"""
Framework Organizer Module
Organizes multiple PDFs into sections and validates framework completeness
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.processing import extract_text_from_pdf

load_dotenv()


def organize_pdfs_by_section(pdf_paths_list: List[str], framework_name: str) -> Dict[str, str]:
    """
    Organize PDFs into sections by analyzing their content using LLM.
    
    Uses LLM to determine section names (part1, part2, rubric, etc.) based on content analysis.
    
    Args:
        pdf_paths_list: List of PDF file paths
        framework_name: Name of the framework
        
    Returns:
        Dictionary mapping section names to PDF paths: {'section_name': 'pdf_path', ...}
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Extract text from each PDF (first 5000 chars for analysis)
    pdf_samples = {}
    for pdf_path in pdf_paths_list:
        try:
            full_text = extract_text_from_pdf(pdf_path)
            # Use first 5000 chars for section identification
            sample_text = full_text[:5000] if len(full_text) > 5000 else full_text
            pdf_samples[pdf_path] = {
                'filename': Path(pdf_path).name,
                'sample': sample_text,
                'full_length': len(full_text)
            }
        except Exception as e:
            print(f"Warning: Could not extract text from {pdf_path}: {e}")
            # Use filename as fallback section name
            pdf_samples[pdf_path] = {
                'filename': Path(pdf_path).name,
                'sample': '',
                'full_length': 0
            }
    
    # Prepare analysis prompt
    pdf_info = []
    for pdf_path, info in pdf_samples.items():
        pdf_info.append({
            'path': pdf_path,
            'filename': info['filename'],
            'sample': info['sample'],
            'length': info['full_length']
        })
    
    analysis_prompt = f"""You are analyzing multiple PDF documents that form parts of a compliance framework.

Framework Name: {framework_name}

Analyze each PDF and determine its section name and role in the framework. Common section types include:
- part1, part2, part3, etc. (main framework parts)
- rubric (evaluation rubric/scoring criteria)
- appendix (appendices)
- guidelines (guidelines or instructions)
- controls (specific controls list)

For each PDF, return:
1. A section name (use lowercase, no spaces, e.g., "part1", "rubric", "appendix")
2. A brief description of its role

PDF Documents to analyze:
{json.dumps(pdf_info, indent=2, ensure_ascii=False)}

Return a JSON object with this structure:
{{
    "sections": [
        {{
            "pdf_path": "path/to/file.pdf",
            "section_name": "part1",
            "description": "Main framework part 1",
            "confidence": "high|medium|low"
        }}
    ]
}}

Analyze each PDF and return the JSON."""
    
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in analyzing compliance framework documents. Identify section types and roles based on content analysis. Always return valid JSON only."
            },
            {
                "role": "user",
                "content": analysis_prompt
            }
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    result_text = response.choices[0].message.content
    
    # Parse JSON response
    try:
        analysis_result = json.loads(result_text)
    except json.JSONDecodeError as e:
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
            analysis_result = json.loads(result_text)
        else:
            raise ValueError(f"Failed to parse JSON response: {e}")
    
    # Build organized sections dictionary
    organized_sections = {}
    for section_info in analysis_result.get("sections", []):
        pdf_path = section_info.get("pdf_path")
        section_name = section_info.get("section_name", "unknown")
        
        # If section name couldn't be determined, use filename (sanitized)
        if section_name == "unknown" or not section_name:
            section_name = Path(pdf_path).stem.lower().replace(" ", "_")
        
        organized_sections[section_name] = pdf_path
    
    # Fallback: if LLM didn't return all PDFs, add missing ones
    for pdf_path in pdf_paths_list:
        if pdf_path not in organized_sections.values():
            # Use filename as section name
            section_name = Path(pdf_path).stem.lower().replace(" ", "_")
            organized_sections[section_name] = pdf_path
    
    return organized_sections


def validate_framework_sections(organized_sections: Dict[str, str], framework_name: str) -> Dict[str, Any]:
    """
    Validate framework sections using LLM-based checks.
    
    Validates:
    - All required sections exist
    - Text quality is sufficient
    - Critical keywords are present
    - Control patterns are detected
    - Proper document structure maintained
    
    Args:
        organized_sections: Dictionary mapping section names to PDF paths
        framework_name: Name of the framework
        
    Returns:
        Dictionary with validation results:
        {
            "status": "pass" | "fail",
            "checks": {...},
            "errors": [...],
            "warnings": [...]
        }
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Extract text from all sections for validation
    section_texts = {}
    total_size = 0
    for section_name, pdf_path in organized_sections.items():
        try:
            text = extract_text_from_pdf(pdf_path)
            section_texts[section_name] = {
                'path': pdf_path,
                'text': text[:10000] if len(text) > 10000 else text,  # Sample for validation
                'full_length': len(text)
            }
            total_size += len(text)
        except Exception as e:
            section_texts[section_name] = {
                'path': pdf_path,
                'text': '',
                'full_length': 0,
                'error': str(e)
            }
    
    validation_prompt = f"""You are validating a compliance framework that has been organized into sections.

Framework Name: {framework_name}
Sections Found: {list(organized_sections.keys())}

IMPORTANT: Do NOT expect specific section names or structures. Different frameworks have different organizations.
Focus on whether the content is useful for compliance evaluation, not whether specific sections exist.

Validate the following aspects:

1. **Content Suitability**: Can compliance controls, requirements, or evaluation criteria be extracted from the text?
   - Look for any compliance-related content (controls, rules, criteria, requirements, standards, guidelines)
   - Check if there's enough content to perform meaningful evaluation
   - DO NOT require specific section names - frameworks vary in structure

2. **Text Quality**: Is the text readable and not corrupted? Are there formatting issues that would prevent extraction?

3. **Evaluation-Relevant Content**: Are there elements that would be useful for evaluating applicant documents?
   - Compliance requirements
   - Control statements
   - Evaluation criteria
   - Scoring rubrics (if present, but not required)
   - Standards or benchmarks

4. **Control Patterns**: Are compliance control patterns detected in the text? (e.g., "must", "shall", "required", numbered controls)

5. **Structure**: Is the document structure logical and coherent? Can sections be understood in context?

Section Texts (samples):
{json.dumps({k: {'length': v['full_length'], 'sample': v['text'][:2000]} for k, v in section_texts.items()}, indent=2, ensure_ascii=False)}

Return a JSON object with this structure:
{{
    "status": "pass" | "fail",
    "checks": {{
        "content_suitability": {{"status": "pass|fail|warning", "details": "..."}},
        "text_quality": {{"status": "pass|fail|warning", "details": "..."}},
        "evaluation_content": {{"status": "pass|fail|warning", "details": "..."}},
        "control_patterns": {{"status": "pass|fail|warning", "details": "..."}},
        "structure": {{"status": "pass|fail|warning", "details": "..."}}
    }},
    "errors": ["error1", "error2", ...],
    "warnings": ["warning1", "warning2", ...],
    "keywords_found": {{"section_name": ["keyword1", ...], ...}}
}}

CRITICAL: Only mark status as "fail" if there are CRITICAL issues:
- Text is completely corrupted or unreadable
- No compliance-related content can be found at all
- Text is too short or empty

Missing optional sections, different naming conventions, or non-standard structures should be warnings, NOT errors.
The framework structure should be flexible - focus on whether controls and evaluation info can be extracted.

Validate the framework sections and return the JSON."""
    
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in validating compliance framework documents. Focus on whether the content contains extractable compliance controls and evaluation criteria. Be flexible about document structure - different frameworks organize content differently. Only fail validation for critical issues like corrupted text or complete absence of compliance content. Always return valid JSON only."
            },
            {
                "role": "user",
                "content": validation_prompt
            }
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    result_text = response.choices[0].message.content
    
    # Parse JSON response
    try:
        validation_result = json.loads(result_text)
    except json.JSONDecodeError as e:
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
            validation_result = json.loads(result_text)
        else:
            raise ValueError(f"Failed to parse JSON response: {e}")
    
    # Add total size to validation result
    validation_result['total_size'] = total_size
    
    # Only fail on critical errors (corrupted text, no content, unreadable)
    # Missing optional sections should be warnings, not errors
    errors = validation_result.get("errors", [])
    warnings = validation_result.get("warnings", [])
    
    # Filter for critical errors only
    critical_keywords = ["corrupted", "unreadable", "no content", "empty", "too short", "cannot extract"]
    critical_errors = [
        e for e in errors 
        if any(keyword in e.lower() for keyword in critical_keywords)
    ]
    
    # Only raise exception for critical errors
    if validation_result.get("status") == "fail" and critical_errors:
        error_msg = f"Framework validation failed for '{framework_name}': " + "; ".join(critical_errors)
        raise ValueError(error_msg)
    elif validation_result.get("status") == "fail" and not critical_errors:
        # If status is fail but no critical errors, downgrade to warning and continue
        print(f"⚠️  Validation warnings for '{framework_name}' (continuing anyway):")
        if warnings:
            for warning in warnings:
                print(f"   - {warning}")
        if errors:
            for error in errors:
                print(f"   - {error}")
        # Change status to pass since we're continuing
        validation_result["status"] = "pass"
    elif warnings:
        # Log warnings but don't fail
        print(f"ℹ️  Validation warnings for '{framework_name}':")
        for warning in warnings:
            print(f"   - {warning}")
    
    return validation_result
