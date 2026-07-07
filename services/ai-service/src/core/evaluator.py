"""
Evaluator Module
Evaluates applicant documents against saved evaluation prompts and controls
"""

import json
import logging
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)


def evaluate_applicant(
    applicant_docs: list[str], evaluation_prompt: str, controls_json: dict[str, Any]
) -> dict[str, Any]:
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

    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

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

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compliance evaluation expert. Evaluate documents against compliance frameworks accurately and provide detailed reports.",
                },
                {"role": "user", "content": evaluation_request},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.error("Evaluator LLM API call failed: %s", e)
        raise

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
                "error": f"Could not parse as JSON: {e}",
            }
