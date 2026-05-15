"""
utils.py — Utility functions: safe JSON parsing, fallbacks, text helpers.
"""

import json
import re
from config import DEFAULT_STATE, MAX_RESPONSE_WORDS


def safe_json_load(text: str, fallback: dict = None) -> dict:
    """
    Safely parse JSON from an LLM response string.
    Handles common issues: markdown fences, leading/trailing text, single quotes.

    Returns parsed dict or the fallback dict on any failure.
    """
    if fallback is None:
        fallback = {}

    if not text:
        return fallback

    # Remove markdown code fences (```json ... ``` or ``` ... ```)
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

    # Try to extract the first JSON object from the string
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Last attempt: replace single quotes with double quotes (common LLM mistake)
    try:
        fixed = cleaned.replace("'", '"')
        return json.loads(fixed)
    except json.JSONDecodeError:
        return fallback


def truncate_to_word_limit(text: str, max_words: int = MAX_RESPONSE_WORDS) -> str:
    """
    Truncate text to approximately max_words words, ending at a sentence boundary.
    """
    words = text.split()
    if len(words) <= max_words:
        return text

    truncated = " ".join(words[:max_words])

    # Try to end at a sentence boundary
    for punct in [".", "!", "?"]:
        last = truncated.rfind(punct)
        if last > len(truncated) // 2:
            return truncated[: last + 1]

    return truncated + "…"


def fallback_five_ps() -> dict:
    """Return the default 5Ps structure as a fallback."""
    import copy
    return copy.deepcopy(DEFAULT_STATE["five_ps"])


def fallback_iks() -> dict:
    """Return a safe default IKS mapping."""
    return {
        "guna": "Rajas",
        "dominant_concepts": ["chitta vritti"],
        "brief_mapping": "The person appears to be in a state of mental agitation.",
    }


def fallback_persona(current_persona: str) -> dict:
    """Keep the current persona if selection fails."""
    return {
        "persona": current_persona,
        "reason": "Maintaining current persona due to a parsing issue.",
    }


def format_risk_badge(risk_level: str) -> str:
    """Return a coloured emoji badge for the risk level."""
    badges = {
        "LOW": "🟢 LOW",
        "MEDIUM": "🟡 MEDIUM",
        "HIGH": "🔴 HIGH",
    }
    return badges.get(risk_level, "⚪ UNKNOWN")


def fallback_response() -> dict:
    """Safe fallback when generate_response fails to parse JSON."""
    return {
        "response_text": (
            "I hear you, and I want to offer support. "
            "Could you tell me a little more about what you are experiencing right now?"
        ),
        "citation_text": "",
        "citation_ref": "",
    }


def parse_response_json(raw: str, max_words: int = None) -> dict:
    """
    Parse the structured JSON returned by build_response_prompt.
    Falls back gracefully if the LLM returns plain text instead of JSON.
    Applies word-limit truncation to response_text.
    """
    result = safe_json_load(raw, fallback=None)

    if result and "response_text" in result:
        if max_words:
            result["response_text"] = truncate_to_word_limit(
                result["response_text"], max_words
            )
        result.setdefault("citation_text", "")
        result.setdefault("citation_ref", "")
        return result

    # LLM returned plain text — treat the whole thing as response_text, no citation
    plain = raw.strip() if raw else ""
    return {
        "response_text": truncate_to_word_limit(plain, max_words) if (plain and max_words) else plain,
        "citation_text": "",
        "citation_ref": "",
    }



