"""
Framework Extraction Module
Extracts compliance controls from PDF text (LLM) and from multiple PDFs in parallel.
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from src.processing import extract_text_from_pdf

load_dotenv()

logger = logging.getLogger(__name__)


def extract_controls_from_framework(
    pdf_text: str, framework_name: str, use_fallback_prompt: bool = False
) -> dict[str, Any]:
    """
    Extract compliance controls from PDF text using LLM.

    Args:
        pdf_text: Extracted text from framework PDF
        framework_name: Name of the framework
        use_fallback_prompt: If True, use a stricter prompt that forbids empty controls (for retries).

    Returns:
        Dictionary with controls array
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")

    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

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
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4.1",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": extraction_prompt},
            ],
            temperature=temperature,
            seed=42,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.error("LLM API call failed for framework '%s': %s", framework_name, e)
        return {"framework_name": framework_name, "controls": []}

    result_text = response.choices[0].message.content
    if not result_text or not str(result_text).strip():
        logger.warning("API returned empty response (possible rate limit or error)")
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
        logger.warning(
            "JSON parsing error: %s. Raw response (len=%d): %r", e, len(result_text or ""), preview
        )
        # Try to fix truncated JSON by finding last complete structure
        last_brace = result_text.rfind("}")
        last_bracket = result_text.rfind("]")
        end_pos = max(last_brace, last_bracket)

        if end_pos > 0:
            try:
                result_json = json.loads(result_text[: end_pos + 1])
                logger.info("Successfully parsed truncated JSON")
            except Exception:
                logger.warning("Could not parse JSON, returning empty controls")
                return {"framework_name": framework_name, "controls": []}
        else:
            return {"framework_name": framework_name, "controls": []}

    # Find controls array - check common keys first
    controls_array: list[dict[str, Any]] = []
    if isinstance(result_json, list):
        controls_array = result_json
    elif isinstance(result_json, dict):
        # Try common keys (including compliance_controls)
        for key in ["controls", "compliance_controls", "items", "data", "Domain"]:
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
        if not controls_array and "id" in result_json:
            controls_array = [result_json]

    return {"framework_name": framework_name, "controls": controls_array}


def extract_controls_from_pdfs(
    pdf_paths_list: list[str], framework_name: str
) -> list[list[dict[str, Any]]]:
    """
    Extract controls from multiple PDFs in parallel.
    Each PDF gets one LLM call.

    Args:
        pdf_paths_list: List of PDF file paths
        framework_name: Name of the framework

    Returns:
        List of controls arrays (one per PDF)
    """
    MAX_RETRIES = 3

    def extract_pdf(pdf_path: str) -> list[dict[str, Any]]:
        """Extract controls from a single PDF. Retries with fallback prompt if empty."""
        try:
            pdf_text = extract_text_from_pdf(pdf_path)
            if not (pdf_text and pdf_text.strip()):
                logger.warning("Skipping %s: no text extracted", pdf_path)
                return []
            controls_json = extract_controls_from_framework(pdf_text, framework_name)
            controls = controls_json.get("controls", [])
            retries = 0
            while len(controls) == 0 and retries < MAX_RETRIES:
                retries += 1
                logger.info(
                    "Empty controls for %s, retry %d/%d with fallback prompt",
                    pdf_path,
                    retries,
                    MAX_RETRIES,
                )
                controls_json = extract_controls_from_framework(
                    pdf_text, framework_name, use_fallback_prompt=True
                )
                controls = controls_json.get("controls", [])
            logger.info("Controls extracted from %s", pdf_path)
            return controls
        except Exception as e:
            logger.error("Error extracting from %s: %s", pdf_path, e)
            return []

    max_workers = min(len(pdf_paths_list), 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        controls_arrays = list(executor.map(extract_pdf, pdf_paths_list))

    return controls_arrays
