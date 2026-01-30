"""
Evaluator Module
Evaluates applicant documents against saved evaluation prompts and controls
"""

import json
from openai import OpenAI
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()


def evaluate_applicant(
    applicant_docs: List[str], 
    evaluation_prompt: str, 
    controls_json: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluate applicant documents against a saved evaluation prompt and controls to produce a structured evaluation report.
    
    Parameters:
        applicant_docs (List[str]): Text contents of applicant documents to evaluate; documents are combined in order and may be truncated if excessively long.
        evaluation_prompt (str): The saved evaluation prompt that defines evaluation criteria and instructions for the model.
        controls_json (Dict[str, Any]): Reference controls/framework as a JSON-serializable dictionary used for context during evaluation.
    
    Returns:
        Dict[str, Any]: The evaluation report parsed from the model's response. On successful JSON parsing this is the structured report (scores, compliance status, etc.). If the model returns non-JSON text that cannot be parsed, returns a fallback dictionary with keys `report_type` set to `"text"`, `content` containing the raw response, and `error` describing the JSON parse failure.
    
    Raises:
        ValueError: If the OPENROUTER_API_KEY environment variable is missing, if the API response is missing or empty, or if the model returns empty content.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Combine all applicant documents
    combined_docs = "\n\n--- Document Separator ---\n\n".join(applicant_docs)
    
    # Truncate if too long
    max_chars = 100000
    if len(combined_docs) > max_chars:
        combined_docs = combined_docs[:max_chars] + "\n\n[Documents truncated due to length...]"
    
    # Create the evaluation request
    evaluation_request = f"""{evaluation_prompt}

---
APPLICANT DOCUMENTS TO EVALUATE:
{combined_docs}

---
CONTROLS REFERENCE (for context):
{json.dumps(controls_json, indent=2, ensure_ascii=False)}

Now evaluate the applicant documents against the framework and provide a comprehensive evaluation report."""

    response = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a compliance evaluation expert. Evaluate documents against compliance frameworks accurately and provide detailed reports."
            },
            {
                "role": "user",
                "content": evaluation_request
            }
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    # Check if response has content
    if not response.choices or not response.choices[0].message:
        raise ValueError(
            f"API returned empty response. Response object: {response}, "
            f"Choices: {getattr(response, 'choices', None)}"
        )
    
    result_text = response.choices[0].message.content
    
    # Check if result_text is None or empty
    if not result_text or not result_text.strip():
        raise ValueError(
            f"API returned empty content. Response: {response}, "
            f"Content: {repr(result_text)}. "
            f"This may indicate an API error, rate limit, or model issue."
        )
    
    # Parse JSON response, handle markdown code blocks if present
    try:
        evaluation_report = json.loads(result_text)
        return evaluation_report
    except json.JSONDecodeError as e:
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
            evaluation_report = json.loads(result_text)
            return evaluation_report
        else:
            return {
                "report_type": "text",
                "content": result_text,
                "error": f"Could not parse as JSON: {e}"
            }