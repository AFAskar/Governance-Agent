"""
Framework Extraction Module
Extracts compliance controls from PDF text (LLM) and from multiple PDFs in parallel.
"""

import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from src.processing import extract_text_from_pdf

load_dotenv()


def extract_controls_from_framework(
    pdf_text: str, framework_name: str, use_fallback_prompt: bool = False
) -> Dict[str, Any]:
    """
    Extract compliance controls from text extracted from a framework PDF.
    
    Parameters:
        pdf_text (str): Full text extracted from the PDF to be analyzed.
        framework_name (str): Name of the framework being processed; included in the returned result.
        use_fallback_prompt (bool): When True, uses a stricter retry prompt that enforces extracting at least one control
            (used for retry attempts when initial extraction yields no controls).
    
    Returns:
        result (Dict[str, Any]): Dictionary with keys:
            - "framework_name" (str): The provided framework_name.
            - "controls" (List[Dict[str, Any]]): List of extracted control objects; each control is a dict expected to
              contain fields such as `id`, `description`, `calculation`, `threshold`, and `scale`. The list is empty
              when no extractable controls are found or parsing fails.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")

    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    schema_and_doc = f"""
### STRICT JSON SCHEMA
Return a JSON object with a single key "controls" whose value is an array. Each control object must have exactly these 5 fields:
- "id": string — Unique alphanumeric identifier (e.g., DSI.OE.01, DG.1).
- "description": string — Clear description of what the control measures, how it applies, and what it covers.
- "calculation": string — Formula or logic for measurement (use empty string "" if not applicable).
- "threshold": string — The minimum passing score or condition (e.g., "70%", "10 days"). Use empty string "" if not applicable.
- "scale": string — Scoring intervals or criteria (e.g., "0-5 scale"). Use empty string "" if not applicable.

Example:
{{
  "controls": [
    {{
      "id": "DSI.OE.01",
      "description": "Measures X; applies to Y.",
      "calculation": "count(events) / total * 100",
      "threshold": "70%",
      "scale": "0-5"
    }}
  ]
}}

### DOCUMENT CONTENT:
{pdf_text}
"""

    if use_fallback_prompt:
        extraction_prompt = f"""
### ROLE
Senior Regulatory Data Architect specializing in GRC (Governance, Risk, and Compliance) systems.

### CRITICAL — RETRY AFTER EMPTY EXTRACTION
A previous extraction attempt for this document returned no controls. You MUST extract at least one control.

- Treat every policy clause, requirement, checklist item, or distinct section as a control.
- Use section headings, numbering, or paragraph labels as control IDs (e.g. "Section 3.1", "Requirement A", "Policy-1").
- If the document is a form or list, each item is a control.
- Return an empty "controls" array ONLY if the document is completely blank or non-text (e.g. images only).
{schema_and_doc}

### OUTPUT
Return ONLY a valid JSON object matching the schema above. No other keys or fields.
"""
        system_content = (
            "You are a Senior Regulatory Data Architect. Extract compliance controls. "
            "Never return an empty 'controls' array unless the document has no extractable content. "
            "Return ONLY valid JSON with a 'controls' array. Each control must have exactly: id, description, calculation, threshold, scale."
        )
        temperature = 0.15
    else:
        extraction_prompt = f"""
### ROLE
Senior Regulatory Data Architect specializing in GRC (Governance, Risk, and Compliance) systems.

### TASK
Extract compliance controls, specifications, and performance metrics from the provided document. Output strictly adheres to the JSON schema below.
{schema_and_doc}

### RULES
1. Extract the full technical detail. Do not paraphrase.
2. Every control in the document must appear in the "controls" array with exactly the 5 fields above.
3. Use empty string "" for calculation, threshold, or scale when the document does not specify them.

### OUTPUT
Return ONLY a valid JSON object matching the schema above. No other keys or fields.
"""
        system_content = "You are a Senior Regulatory Data Architect. Extract compliance controls. Return ONLY valid JSON with a 'controls' array. Each control must have exactly: id, description, calculation, threshold, scale."
        temperature = 0.15

    # Low temperature + fixed seed for reproducible, consistent extraction
    response = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": extraction_prompt},
        ],
        temperature=temperature,
        seed=42,
        response_format={"type": "json_object"}
    )

    result_text = response.choices[0].message.content
    if not result_text or not str(result_text).strip():
        print("API returned empty response (possible rate limit or error)")
        return {"framework_name": framework_name, "controls": []}

    result_text = str(result_text).strip()

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
        preview = (result_text or "")[:200]
        print(f"Warning: JSON parsing error: {e}. Raw response (len={len(result_text or '')}): {preview!r}")
        # Try to fix truncated JSON by finding last complete structure
        last_brace = result_text.rfind('}')
        last_bracket = result_text.rfind(']')
        end_pos = max(last_brace, last_bracket)

        if end_pos > 0:
            try:
                result_json = json.loads(result_text[:end_pos + 1])
                print("Successfully parsed truncated JSON")
            except Exception:
                print("Could not parse JSON, returning empty controls")
                return {"framework_name": framework_name, "controls": []}
        else:
            return {"framework_name": framework_name, "controls": []}

    # Find controls array - check common keys first
    controls_array: List[Dict[str, Any]] = []
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


def extract_controls_from_pdfs(
    pdf_paths_list: List[str], framework_name: str
) -> List[List[Dict[str, Any]]]:
    """
    Extract controls from each PDF path in pdf_paths_list using the LLM in parallel.
    
    Returns:
        List[List[Dict[str, Any]]]: A list where each element is the extracted controls list for the corresponding PDF in pdf_paths_list. Empty list for PDFs that failed or produced no controls.
    """
    MAX_RETRIES = 3

    def extract_pdf(pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extracts compliance controls from a single PDF file.
        
        Attempts to extract text from the PDF and parse controls for the current framework. If the initial extraction yields no controls, retries up to MAX_RETRIES using a stricter fallback prompt to force extraction. Returns an empty list if no text is found, if extraction fails after retries, or if an exception occurs.
        
        Parameters:
            pdf_path (str): Path to the PDF file to process.
        
        Returns:
            List[Dict[str, Any]]: A list of extracted control objects (possibly empty).
        """
        try:
            pdf_text = extract_text_from_pdf(pdf_path)
            if not (pdf_text and pdf_text.strip()):
                print(f"Skipping {pdf_path}: no text extracted")
                return []
            controls_json = extract_controls_from_framework(pdf_text, framework_name)
            controls = controls_json.get("controls", [])
            retries = 0
            while len(controls) == 0 and retries < MAX_RETRIES:
                retries += 1
                print(f"Empty controls for {pdf_path}, retry {retries}/{MAX_RETRIES} with fallback prompt")
                controls_json = extract_controls_from_framework(
                    pdf_text, framework_name, use_fallback_prompt=True
                )
                controls = controls_json.get("controls", [])
            print(f"Controls extracted from {pdf_path}")
            return controls
        except Exception as e:
            print(f"Error extracting from {pdf_path}: {e}")
            return []

    with ThreadPoolExecutor(max_workers=len(pdf_paths_list)) as executor:
        controls_arrays = list(executor.map(extract_pdf, pdf_paths_list))

    return controls_arrays