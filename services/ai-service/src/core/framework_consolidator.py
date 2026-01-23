"""
Framework Consolidator Module
Extracts controls from sections and creates a master evaluation prompt
"""

import json
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.processing import extract_text_from_pdf
from src.core.framework_extractor import extract_controls_from_framework

load_dotenv()


def extract_controls_from_sections(organized_sections: Dict[str, str], framework_name: str) -> Dict[str, Dict[str, Any]]:
    """
    Extract controls from each section by calling extract_controls_from_framework for each.
    
    Args:
        organized_sections: Dictionary mapping section names to PDF paths
        framework_name: Name of the framework
        
    Returns:
        Dictionary mapping section names to their controls JSON:
        {'section_name': controls_json, ...}
    """
    section_controls = {}
    
    for section_name, pdf_path in organized_sections.items():
        try:
            # Extract text from PDF
            pdf_text = extract_text_from_pdf(pdf_path)
            
            # Extract controls for this section
            controls_json = extract_controls_from_framework(pdf_text, f"{framework_name}_{section_name}")
            
            # Add section context to controls
            controls_json['section_name'] = section_name
            controls_json['section_path'] = pdf_path
            
            section_controls[section_name] = controls_json
            
        except Exception as e:
            print(f"Warning: Failed to extract controls from section '{section_name}' ({pdf_path}): {e}")
            # Mark section as incomplete
            section_controls[section_name] = {
                'section_name': section_name,
                'section_path': pdf_path,
                'error': str(e),
                'incomplete': True
            }
    
    return section_controls


def create_master_prompt(
    section_controls: Dict[str, Dict[str, Any]], 
    organized_sections: Dict[str, str], 
    framework_name: str
) -> str:
    """
    Create a master evaluation prompt by consolidating all section controls and texts.
    
    Uses LLM to consolidate all section controls into a unified master prompt with:
    - Full text from each section (organized by section)
    - Combined extracted controls
    - Unified evaluation rules
    - Rubric/scoring criteria from all sections
    
    Args:
        section_controls: Dictionary mapping section names to their controls JSON
        organized_sections: Dictionary mapping section names to PDF paths
        framework_name: Name of the framework
        
    Returns:
        Master evaluation prompt string
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Extract text from each section (with aggressive truncation to stay under token limits)
    section_texts = {}
    for section_name, pdf_path in organized_sections.items():
        try:
            text = extract_text_from_pdf(pdf_path)
            # Reduce to 10000 chars per section to stay under token limits
            if len(text) > 10000:
                text = text[:10000] + "\n\n[Text truncated - see full content in original PDFs]"
            section_texts[section_name] = text
        except Exception as e:
            print(f"Warning: Could not extract text from {pdf_path}: {e}")
            section_texts[section_name] = ""
    
    # Prepare summaries instead of full data to reduce token usage
    section_summaries = []
    total_controls = 0
    
    for section_name in organized_sections.keys():
        controls = section_controls.get(section_name, {})
        controls_list = controls.get('controls', []) if not controls.get('incomplete') else []
        total_controls += len(controls_list)
        
        # Create summary instead of full JSON
        section_summary = {
            'section_name': section_name,
            'text_sample': section_texts.get(section_name, '')[:5000],  # Only 5k chars
            'controls_count': len(controls_list),
            'controls_summary': [
                {
                    'id': c.get('id', ''),
                    'title': c.get('title', '')[:100],  # Truncate titles
                    'category': c.get('category', '')
                }
                for c in controls_list[:20]  # Only first 20 controls per section
            ]
        }
        section_summaries.append(section_summary)
    
    consolidation_prompt = f"""You are creating a master evaluation prompt for a compliance framework.

Framework Name: {framework_name}
Total Sections: {len(organized_sections)}
Total Controls: {total_controls}

Create a comprehensive master evaluation prompt that:
1. Provides clear evaluation instructions
2. References all sections and their key controls
3. Includes unified evaluation rules
4. Provides rubric/scoring guidance

Section Summaries:
{json.dumps(section_summaries, indent=2, ensure_ascii=False)}

Create the master prompt. Structure it as:

# FRAMEWORK: {framework_name}

## EVALUATION INSTRUCTIONS
[Clear instructions for evaluating applicant documents]

## FRAMEWORK SECTIONS OVERVIEW
[Brief overview of each section and its purpose]

## EVALUATION RULES
[Unified rules combining all sections]

## RUBRIC & SCORING
[Evaluation criteria and scoring guidance]

## CONTROLS REFERENCE
[Summary of key controls to evaluate]

NOTE: The full framework text is available in the original PDFs. This prompt focuses on evaluation methodology and key controls.

Create the master evaluation prompt now."""
    
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in creating comprehensive evaluation prompts for compliance frameworks. Consolidate multiple sections into a unified, well-structured master prompt. The prompt should be clear, complete, and ready to use."
            },
            {
                "role": "user",
                "content": consolidation_prompt
            }
        ],
        temperature=0.3
    )
    
    master_prompt = response.choices[0].message.content.strip()
    
    # If the LLM response is too short, build prompt manually
    if len(master_prompt) < 2000:
        master_prompt = f"# FRAMEWORK: {framework_name}\n\n"
        master_prompt += "## EVALUATION INSTRUCTIONS\n\n"
        master_prompt += "Evaluate applicant documents against all sections of this framework.\n\n"
        
        for section_name, text in section_texts.items():
            master_prompt += f"## {section_name.upper()}\n\n{text}\n\n"
        
        master_prompt += "\n## CONTROLS SUMMARY\n\n"
        for section_name, controls in section_controls.items():
            if not controls.get('incomplete'):
                master_prompt += f"### {section_name.upper()}\n\n"
                for control in controls.get('controls', [])[:10]:
                    master_prompt += f"- {control.get('title', 'Control')}\n"
    
    return master_prompt
