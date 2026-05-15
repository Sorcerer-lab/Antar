"""
risk.py — Hybrid risk detection: keyword fast-path + LLM semantic scorer.

Two-layer architecture:
    Layer 1 (keyword):  Instant. Catches explicit crisis language.
                        Hard safety net — always runs, never removed.
    Layer 2 (semantic): LLM call with conversation context.
                        Catches indirect, coded, or passive expressions of distress.

Final decision logic:
    HIGH   → either layer says HIGH, or passive_ideation + hopelessness signals
             together elevate a MEDIUM keyword result
    MEDIUM → semantic says MEDIUM with confidence >= 0.6, or keyword says MEDIUM
    LOW    → everything else
"""

import json
import re
from config import HIGH_RISK_KEYWORDS, MEDIUM_RISK_KEYWORDS


# ─── Layer 1: Keyword fast-path ───────────────────────────────────────────────

def _keyword_risk(text: str) -> str:
    """Instant keyword scan. Returns 'HIGH', 'MEDIUM', or 'LOW'."""
    lowered = text.lower()
    if any(kw in lowered for kw in HIGH_RISK_KEYWORDS):
        return "HIGH"
    if any(kw in lowered for kw in MEDIUM_RISK_KEYWORDS):
        return "MEDIUM"
    return "LOW"


def quick_risk_check(text: str) -> bool:
    """
    Fast pre-flight check used by orchestrator BEFORE the semantic call.
    Returns True if keywords alone indicate HIGH risk — triggers immediate
    escalation without waiting for the LLM.
    """
    return _keyword_risk(text) == "HIGH"


# ─── Layer 2: LLM semantic scorer ────────────────────────────────────────────

def build_risk_prompt(user_message: str, conversation_history: list) -> str:
    """
    Build the prompt for semantic risk assessment.
    Returns structured JSON with risk_level, confidence, reasoning, and signal flags.
    """
    history_lines = []
    for m in conversation_history[-6:]:  # last 3 turns for context
        role = "User" if m["role"] == "user" else "Assistant"
        history_lines.append(f"{role}: {m['content']}")
    history_str = "\n".join(history_lines) if history_lines else "(No prior conversation)"

    return f"""You are a mental health risk assessment specialist. Your task is to evaluate
the risk level in a user's message from a mental wellness chatbot conversation.

## CONVERSATION HISTORY (last 3 turns)
{history_str}

## CURRENT USER MESSAGE
"{user_message}"

## TASK
Assess the mental health risk level considering:
- Explicit statements (direct mentions of self-harm, suicide, hopelessness)
- Implicit signals (passive ideation, coded language, withdrawal themes)
- Contextual escalation (worsening tone across conversation history)
- Protective factors mentioned (support systems, future plans, coping)

## RISK LEVELS
- HIGH: Active suicidal ideation, self-harm intent, immediate danger signals,
        statements like "I don't want to be here", "everyone would be better off",
        "I've been thinking about ending it", passive ideation with hopelessness.
- MEDIUM: Significant distress, hopelessness, isolation, passive statements like
          "what's the point", "I'm so tired of everything", "no one would notice",
          emotional crisis without immediate danger signals.
- LOW: General distress, stress, sadness, anxiety — normal wellness conversation range.

## SIGNAL FLAGS (set to true if detected)
- passive_ideation: indirect or coded expressions of not wanting to exist
- hopelessness: pervasive sense that nothing will improve
- isolation: feeling completely cut off from others
- escalation: message is notably more distressed than prior turns

RETURN ONLY valid JSON. No markdown, no explanation, nothing outside the JSON.

{{
  "risk_level": "HIGH" | "MEDIUM" | "LOW",
  "confidence": 0.0 to 1.0,
  "reasoning": "One sentence explaining the primary signal detected.",
  "signals": {{
    "passive_ideation": true | false,
    "hopelessness": true | false,
    "isolation": true | false,
    "escalation": true | false
  }}
}}"""


def _parse_semantic_result(raw: str) -> dict:
    """
    Safely parse the LLM's JSON risk output.
    Returns a LOW-risk fallback dict on any parse failure.
    """
    fallback = {
        "risk_level": "LOW",
        "confidence": 0.5,
        "reasoning": "Could not parse semantic risk assessment; defaulting to LOW.",
        "signals": {
            "passive_ideation": False,
            "hopelessness": False,
            "isolation": False,
            "escalation": False,
        },
    }
    if not raw:
        return fallback

    cleaned = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        parsed = json.loads(cleaned)
        if "risk_level" not in parsed or parsed["risk_level"] not in ("HIGH", "MEDIUM", "LOW"):
            return fallback
        parsed["confidence"] = max(0.0, min(1.0, float(parsed.get("confidence", 0.5))))
        if "signals" not in parsed:
            parsed["signals"] = fallback["signals"]
        return parsed
    except (json.JSONDecodeError, ValueError, TypeError):
        return fallback


# ─── Main: Hybrid detect_risk ────────────────────────────────────────────────

def detect_risk(user_message: str, conversation_history: list, call_llm_fn) -> dict:
    """
    Full hybrid risk detection. Returns a rich result dict consumed by orchestrator.

    Args:
        user_message:         The user's current message.
        conversation_history: List of prior messages from state.
        call_llm_fn:          The call_llm function from orchestrator (injected
                              to avoid circular imports).

    Returns:
        {
            "risk_level":  "HIGH" | "MEDIUM" | "LOW",
            "source":      "keyword" | "semantic" | "hybrid",
            "confidence":  float,
            "reasoning":   str,
            "signals":     { passive_ideation, hopelessness, isolation, escalation }
        }
    """
    keyword_result = _keyword_risk(user_message)

    # Layer 1 hard stop: explicit HIGH keyword → escalate immediately, no LLM call.
    if keyword_result == "HIGH":
        return {
            "risk_level": "HIGH",
            "source": "keyword",
            "confidence": 1.0,
            "reasoning": "Explicit high-risk language detected in message.",
            "signals": {
                "passive_ideation": False,
                "hopelessness": False,
                "isolation": False,
                "escalation": False,
            },
        }

    # Layer 2: semantic LLM assessment
    try:
        prompt = build_risk_prompt(user_message, conversation_history)
        raw = call_llm_fn(prompt)
        semantic = _parse_semantic_result(raw)
    except Exception as e:
        print(f"[detect_risk] semantic scorer failed: {e} — keyword fallback used")
        semantic = {
            "risk_level": keyword_result,
            "confidence": 0.5,
            "reasoning": "Semantic scorer unavailable; keyword fallback applied.",
            "signals": {
                "passive_ideation": False,
                "hopelessness": False,
                "isolation": False,
                "escalation": False,
            },
        }

    semantic_level = semantic["risk_level"]
    semantic_conf = semantic["confidence"]

    # ── Decision logic ────────────────────────────────────────────────────────
    if semantic_level == "HIGH":
        # Semantic sees active ideation — escalate regardless of confidence
        final_level, source = "HIGH", "semantic"

    elif (
        keyword_result == "MEDIUM"
        and semantic["signals"].get("passive_ideation")
        and semantic["signals"].get("hopelessness")
    ):
        # Keyword MEDIUM + passive ideation + hopelessness → elevate to HIGH
        final_level, source = "HIGH", "hybrid"

    elif semantic_level == "MEDIUM" and semantic_conf >= 0.6:
        # Semantic confident about MEDIUM distress
        final_level, source = "MEDIUM", "semantic"

    elif keyword_result == "MEDIUM":
        # Keyword said MEDIUM but semantic isn't confident — keep MEDIUM conservatively
        final_level, source = "MEDIUM", "keyword"

    else:
        final_level, source = "LOW", "semantic"

    return {
        "risk_level": final_level,
        "source": source,
        "confidence": semantic_conf,
        "reasoning": semantic.get("reasoning", ""),
        "signals": semantic.get("signals", {}),
    }


# ─── Escalation response ─────────────────────────────────────────────────────

def escalation_response() -> str:
    """
    Compassionate crisis escalation message shown when risk_level is HIGH.
    No persona, no analysis — immediate human support signposting only.
    """
    return (
        "💛 I hear you, and what you're feeling matters deeply.\n\n"
        "It sounds like you may be going through something very painful right now. "
        "Please know you are not alone, and support is available right now.\n\n"
        "**Please reach out immediately:**\n"
        "- 🇮🇳 **iCall (India):** 9152987821\n"
        "- 🌐 **Vandrevala Foundation (24/7):** 1860-2662-345\n"
        "- 🌍 **International Association for Suicide Prevention:** "
        "[https://www.iasp.info/resources/Crisis_Centres/](https://www.iasp.info/resources/Crisis_Centres/)\n\n"
        "If you are in immediate danger, please call emergency services (112 in India) "
        "or go to your nearest hospital.\n\n"
        "You are worth every effort. 🙏"
    )
