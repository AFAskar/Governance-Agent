"""
Prompt Generator Module
Generates evaluation prompts from extracted controls JSON
"""

import json
from openai import OpenAI
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()


def generate_evaluation_prompt(controls_json: Dict[str, Any], framework_name: str) -> str:
    """
    Generate an evaluation prompt from extracted controls JSON.
    
    The prompt will contain framework logic and clear evaluation criteria
    that can be used directly for applicant evaluation.
    
    Args:
        controls_json: Dictionary containing extracted controls, metadata, and filters
        framework_name: Name of the framework
        
    Returns:
        Evaluation prompt string ready to use for applicant evaluation
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Convert controls JSON to string for the prompt
    controls_str = json.dumps(controls_json, indent=2, ensure_ascii=False)
    
    generation_prompt = f"""You are an expert in compliance evaluation. Based on the extracted compliance framework controls below, 
create a comprehensive evaluation prompt that will be used to evaluate applicant documents against this framework.

Framework Name: {framework_name}

The evaluation prompt should:
1. Clearly explain the framework and its purpose
2. List all controls/rules/criteria that need to be evaluated
3. Provide clear evaluation criteria for each control
4. Specify how to score or assess compliance (e.g., compliant/non-compliant, or scoring scale)
5. Include instructions for handling multilingual documents (Arabic/English)
6. Be structured so it can be used directly with an LLM to evaluate applicant documents
7. Include instructions on how to format the evaluation report

The prompt should be self-contained and can be used independently to evaluate any applicant's documents.

Extracted Controls JSON:
{controls_str}

Generate the evaluation prompt now. The prompt should be clear, comprehensive, and ready to use."""

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in creating evaluation prompts for compliance frameworks. Create clear, comprehensive prompts that can be used to evaluate documents against compliance standards."
            },
            {
                "role": "user",
                "content": generation_prompt
            }
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content.strip()
