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
    Evaluate applicant documents using the saved evaluation prompt and controls.
    
    Args:
        applicant_docs: List of text content from applicant documents
        evaluation_prompt: Saved evaluation prompt from setup phase
        controls_json: Saved controls JSON from setup phase
        
    Returns:
        Dictionary containing evaluation report with scores/compliance status
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
        model="deepseek/deepseek-r1",
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
    
    result_text = response.choices[0].message.content
    
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
