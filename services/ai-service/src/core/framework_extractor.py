"""
Framework Extractor Module
Uses LLM to extract compliance controls/rules/criteria from framework PDF text
"""

import json
from openai import OpenAI
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


def extract_controls_from_framework(pdf_text: str, framework_name: str) -> Dict[str, Any]:
    """
    Extract compliance controls, rules, and criteria from framework PDF text using LLM.
    
    Handles multilingual content (Arabic/English) and identifies controls regardless
    of terminology used (controls, rules, criteria, etc.).
    
    Args:
        pdf_text: Extracted text from framework PDF
        framework_name: Name of the framework being processed
        
    Returns:
        Dictionary with structure:
        {
            "framework_name": str,
            "controls": [...],
            "metadata": {...},
            "filters": {...}
        }
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Truncate text if too long (model has context limits)
    # Keep first ~100k characters to ensure we capture the framework structure
    max_chars = 100000
    if len(pdf_text) > max_chars:
        pdf_text = pdf_text[:max_chars] + "\n\n[Text truncated due to length...]"
    
    extraction_prompt = f"""You are an expert in compliance frameworks and regulatory standards. 
Your task is to extract compliance controls, rules, criteria, or requirements from the following framework document.

Framework Name: {framework_name}

The document may be in Arabic, English, or both. The terminology may vary:
- Controls (ضوابط)
- Rules (قواعد)
- Criteria (معايير)
- Requirements (متطلبات)
- Standards (معايير)

Extract ALL compliance-related items regardless of what they're called in the document.

Return a JSON object with the following structure:
{{
    "framework_name": "{framework_name}",
    "controls": [
        {{
            "id": "unique identifier or number",
            "title": "control title in original language",
            "description": "detailed description of the control/rule/criteria",
            "category": "category or domain",
            "language": "ar" or "en" or "both"
        }}
    ],
    "metadata": {{
        "total_controls": number,
        "extraction_date": "ISO format date",
        "languages_detected": ["ar", "en"],
        "framework_type": "type of framework"
    }},
    "filters": {{
        "categories": ["list of unique categories"],
        "domains": ["list of unique domains if available"]
    }}
}}

Document text:
{pdf_text}

Extract the compliance controls/rules/criteria and return ONLY valid JSON, no additional text."""

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1",
        messages=[
            {
                "role": "system",
                "content": "You are a compliance framework expert. Extract structured compliance controls from documents. Always return valid JSON only."
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
    
    # Parse JSON response, handle markdown code blocks if present
    try:
        controls_json = json.loads(result_text)
        return controls_json
    except json.JSONDecodeError as e:
        if "```json" in result_text:
            json_start = result_text.find("```json") + 7
            json_end = result_text.find("```", json_start)
            result_text = result_text[json_start:json_end].strip()
            controls_json = json.loads(result_text)
            return controls_json
        else:
            raise ValueError(f"Failed to parse JSON response: {e}")
