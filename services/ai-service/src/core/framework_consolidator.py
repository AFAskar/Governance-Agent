"""
Framework Consolidator Module
Merges controls from multiple sections into a master framework
"""

import json
from typing import Dict, Any, List
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.processing import extract_text_from_pdf
from src.core.framework_extractor import extract_controls_from_framework
from concurrent.futures import ThreadPoolExecutor

load_dotenv()


def extract_controls_from_pdfs(pdf_paths_list: List[str], framework_name: str) -> List[List[Dict[str, Any]]]:
    """
    Extract controls from multiple PDFs in parallel.
    Each PDF gets one LLM call.
    
    Args:
        pdf_paths_list: List of PDF file paths
        framework_name: Name of the framework
        
    Returns:
        List of controls arrays (one per PDF)
    """
    def extract_pdf(pdf_path: str):
        """Extract controls from a single PDF."""
        try:
            pdf_text = extract_text_from_pdf(pdf_path)
            controls_json = extract_controls_from_framework(pdf_text, framework_name)
            return controls_json.get("controls", [])
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            return []
    
    # Process all PDFs in parallel
    with ThreadPoolExecutor(max_workers=len(pdf_paths_list)) as executor:
        controls_arrays = list(executor.map(extract_pdf, pdf_paths_list))
    
    return controls_arrays


def compose_master_framework(json_list: List[Dict[str, Any]], framework_name: str) -> Dict[str, Any]:
    """
    Merge multiple JSON arrays into a single Master Framework.
    
    Args:
        json_list: List of controls arrays from different sections
        framework_name: Name of the framework
        
    Returns:
        Single master framework JSON object
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Prepare JSON for prompt
    json_list_str = json.dumps(json_list, indent=2, ensure_ascii=False)
    if len(json_list_str) > 50000:
        json_list_str = json_list_str[:50000] + "\n\n[Data truncated...]"
    
    composition_prompt = f"""### ROLE: JSON Integrator & Data Architect
### TASK: Merge these {len(json_list)} JSON arrays into a single Master Framework.
### INSTRUCTIONS:
1. Take all controls from the input arrays and combine them into a single flat array.
2. De-duplicate IDs: If a Control exists in multiple files, merge the descriptions (keep the most complete version).
3. Return a JSON object with this structure:
   {{
     "framework_name": "{framework_name}",
     "controls": [array of all merged controls]
   }}
4. DO NOT create Domain structures or nested hierarchies - just a flat array of controls.
### INPUT DATA:
{json_list_str}

### OUTPUT
Return ONLY a JSON object with "framework_name" and "controls" keys. The "controls" must be a flat array of all controls from the input."""
    
    response = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a JSON Integrator. Merge multiple JSON arrays into a single master framework. Return valid JSON only."
            },
            {
                "role": "user",
                "content": composition_prompt
            }
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    result_text = response.choices[0].message.content
    print("\n" + "="*60)
    print("COMPOSITION RESPONSE:")
    print("="*60)
    print(result_text)
    print("="*60 + "\n")
    
    master_framework = json.loads(result_text)
    
    # Find controls array from any key
    controls_array = []
    if isinstance(master_framework, dict):
        # Check common keys first
        for key in ['controls', 'compliance_controls', 'items', 'data']:
            if key in master_framework and isinstance(master_framework[key], list):
                controls_array = master_framework[key]
                break
        
        # If Domain structure, extract controls from it
        if not controls_array and 'Domain' in master_framework:
            domain_list = master_framework['Domain']
            if isinstance(domain_list, list):
                # Flatten controls from all domains
                for domain in domain_list:
                    if isinstance(domain, dict) and 'Controls' in domain:
                        if isinstance(domain['Controls'], list):
                            controls_array.extend(domain['Controls'])
        
        # If still not found, find any array
        if not controls_array:
            for value in master_framework.values():
                if isinstance(value, list) and len(value) > 0:
                    # Check if it's a list of control objects (have 'id' field)
                    if all(isinstance(item, dict) and 'id' in item for item in value):
                        controls_array = value
                        break
    
    # Normalize to controls key
    master_framework["framework_name"] = framework_name
    master_framework["controls"] = controls_array
    
    return master_framework
