"""
Framework Extractor Module
Extracts compliance controls from PDF text using LLM
"""

import json
from openai import OpenAI
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


def extract_controls_from_framework(pdf_text: str, framework_name: str) -> Dict[str, Any]:
    """
    Extract compliance controls from PDF text using LLM.
    
    Args:
        pdf_text: Extracted text from framework PDF
        framework_name: Name of the framework
        
    Returns:
        Dictionary with controls array
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    extraction_prompt = f"""
### ROLE
Senior Regulatory Data Architect specializing in GRC (Governance, Risk, and Compliance) systems.

### TASK
Perform a high-fidelity extraction of compliance controls, specifications, and performance metrics from the provided document.

### SCHEMA CONSTRAINTS
For each identified item, you must populate the following JSON structure:
- "id": Unique alphanumeric identifier (e.g., DSI.OE.01, DG.1).
- "title": Original title from the text.
- "type": Classify as 'Administrative Policy', 'Technical Control', or 'Performance Metric'.
- "semantic_intent": The underlying goal or risk this item addresses (often found in "This aims to..." sections).
- "description": A clear, concise description of this measurement or control—what it measures, how it applies, and what it covers.
- "requirements": A list of specific, actionable conditions that must be met.
- "evaluation_logic": {{
    "calculation": "Formula or logic for measurement (if applicable)",
    "threshold": "The minimum passing score or condition (e.g., 70%, 10 days)",
    "scale": "Scoring intervals (e.g., 0-5 scale criteria)"
}}
- "evidence_suggested": Examples of artifacts needed to prove compliance (e.g., API logs, DMO charter).

### EXTRACTION RULES
1. **No Summarization:** Extract the full technical detail. Do not paraphrase.
2. **Multilingual Mapping:** If a control is in Arabic, maintain the 'title' in Arabic but provide a technical English summary in 'semantic_intent'.
3. **Description:** For every control, write a "description" that explains what the measurement covers, how it applies, and what it measures. Keep it concise but complete.
4. **Hierarchy:** If a control has sub-specifications, nest them within a 'sub_controls' array.

### DOCUMENT CONTENT:
{pdf_text}

### OUTPUT
Return ONLY a valid JSON object. Ensure every ID in the document is represented.
"""

    response = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a Senior Regulatory Data Architect. Extract compliance controls and return valid JSON only."
            },
            {
                "role": "user",
                "content": extraction_prompt
            }
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    result_text = response.choices[0].message.content
    print("\n" + "="*60)
    print("EXTRACTION RESPONSE:")
    print("="*60)
    print(result_text)
    print("="*60 + "\n")
    
    # Try to extract JSON from markdown code blocks first
    if "```json" in result_text:
        json_start = result_text.find("```json") + 7
        json_end = result_text.find("```", json_start)
        if json_end > json_start:
            result_text = result_text[json_start:json_end].strip()
    
    # Parse JSON with error handling
    try:
        result_json = json.loads(result_text)
    except json.JSONDecodeError as e:
        print(f"Warning: JSON parsing error: {e}")
        # Try to fix truncated JSON by finding last complete structure
        last_brace = result_text.rfind('}')
        last_bracket = result_text.rfind(']')
        end_pos = max(last_brace, last_bracket)
        
        if end_pos > 0:
            try:
                result_json = json.loads(result_text[:end_pos + 1])
                print("Successfully parsed truncated JSON")
            except:
                print("Could not parse JSON, returning empty controls")
                return {"framework_name": framework_name, "controls": []}
        else:
            return {"framework_name": framework_name, "controls": []}
    
    # Find controls array - check common keys first
    controls_array = []
    if isinstance(result_json, list):
        controls_array = result_json
    elif isinstance(result_json, dict):
        # Try common keys (including compliance_controls)
        for key in ['controls', 'compliance_controls', 'items', 'data', 'Domain']:
            if key in result_json and isinstance(result_json[key], list):
                controls_array = result_json[key]
                break
        
        # If not found, find any array
        if not controls_array:
            for value in result_json.values():
                if isinstance(value, list) and len(value) > 0:
                    controls_array = value
                    break
        
        # If still not found and it's a single control object, wrap it in array
        if not controls_array and 'id' in result_json:
            controls_array = [result_json]
    
    return {
        "framework_name": framework_name,
        "controls": controls_array
    }
