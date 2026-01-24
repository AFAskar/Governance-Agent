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
    
    Args:
        controls_json: Dictionary containing extracted controls
        framework_name: Name of the framework
        
    Returns:
        Evaluation prompt string
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Convert controls JSON to string
    controls_str = json.dumps(controls_json, indent=2, ensure_ascii=False)
    if len(controls_str) > 50000:
        controls_str = controls_str[:50000] + "\n\n[Data truncated...]"
    
    generation_prompt = f"""
### ROLE
Prompt Engineer & Compliance Auditor.

### TASK
Using the provided Master JSON containing multiple compliance frameworks, generate a sophisticated **System Prompt** for an "AI Compliance Auditor."

### SYSTEM PROMPT REQUIREMENTS
The generated prompt must instruct the AI Auditor to:
1. **Role Adoption:** Act as a lead auditor for Saudi National Data Governance (NDMO) and Operational Excellence (SDAIA).
2. **Cross-Framework Mapping:** When evaluating a document, identify which controls from WHICH framework apply (e.g., mapping user evidence to both a Policy and an OE Metric).
3. **Evidence Analysis Logic:**
    - Step A: Extract claims from the applicant's document.
    - Step B: Compare claims against the 'Requirements' and 'Thresholds' in the Master JSON.
    - Step C: Check for specific 'Evidence Suggested' artifacts.
4. **Scoring Protocol:** Apply the strict 0-5 scale for metrics and binary (Compliant/Non-Compliant) for policies as defined in the source data.
5. **Gap Analysis:** For every non-compliant item, specify exactly what is missing based on the 'Semantic Intent'.

### SOURCE FRAMEWORKS (JSON):
{controls_str}

### FINAL OUTPUT
Generate the full System Prompt text. The prompt should be optimized for a model with a large context window and include instructions on generating a 'Compliance Gap Report' table at the end of every evaluation.
"""

    response = client.chat.completions.create(
        model="openai/gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You are a Prompt Engineer & Compliance Auditor. Generate sophisticated system prompts for AI Compliance Auditors."
            },
            {
                "role": "user",
                "content": generation_prompt
            }
        ],
        temperature=0.3
    )
    
    result_text = response.choices[0].message.content.strip()
    print("\n" + "="*60)
    print("PROMPT GENERATION RESPONSE:")
    print("="*60)
    print(result_text)
    print("="*60 + "\n")
    
    return result_text
