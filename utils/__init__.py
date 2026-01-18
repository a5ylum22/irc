"""Utility functions for the Investment Research Co-Pilot."""

import json
import re


def clean_json_response(response_text: str) -> str:
    """
    Clean LLM response to extract pure JSON.
    
    Handles:
    - Markdown code blocks (```json ... ```)
    - Extra whitespace
    - Text before/after JSON
    
    Args:
        response_text: Raw response from LLM
        
    Returns:
        Cleaned JSON string
    """
    # Strip whitespace
    response_text = response_text.strip()
    
    # Remove markdown code blocks
    if response_text.startswith("```"):
        # Find the start of JSON (after ```json or ```)
        lines = response_text.split('\n')
        if lines[0].startswith("```"):
            lines = lines[1:]  # Remove first ```json or ``` line
        
        # Remove closing ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        
        response_text = '\n'.join(lines).strip()
    
    # Try to extract JSON object if there's extra text
    # Look for { ... } pattern
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        response_text = json_match.group(0)
    
    return response_text


def parse_llm_json(response_text: str, fallback: dict = None) -> dict:
    """
    Parse JSON from LLM response with error handling.
    
    Args:
        response_text: Raw response from LLM
        fallback: Fallback dict if parsing fails
        
    Returns:
        Parsed dict or fallback
    """
    try:
        cleaned = clean_json_response(response_text)
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: Failed to parse JSON: {e}")
        if fallback:
            return fallback
        # Return the raw text in a dict
        return {"raw_response": response_text}