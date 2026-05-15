"""
state_manager.py — Manages conversation state across the session.
"""

import copy
from config import DEFAULT_STATE


def initialize_state() -> dict:
    """Return a fresh deep copy of the default state."""
    return copy.deepcopy(DEFAULT_STATE)


def append_message(state: dict, role: str, content: str) -> dict:
    """
    Append a message to the conversation history.
    role: 'user' | 'assistant'
    """
    state["messages"].append({"role": role, "content": content})
    return state


def reset_state() -> dict:
    """Reset to a clean initial state."""
    return initialize_state()


def update_risk(state: dict, level: str, risk_detail: dict = None) -> dict:
    """
    Update the risk level and optionally store the full semantic risk detail.
    level: 'LOW' | 'MEDIUM' | 'HIGH'
    risk_detail: full dict from detect_risk (source, confidence, reasoning, signals)
    """
    state["risk_level"] = level
    if risk_detail:
        state["risk_detail"] = risk_detail
    return state


def update_five_ps(state: dict, five_ps: dict) -> dict:
    """Merge new 5Ps into state, keeping old values for any missing keys."""
    for key in DEFAULT_STATE["five_ps"]:
        if key in five_ps and five_ps[key]:
            state["five_ps"][key] = five_ps[key]
    return state


def update_iks(state: dict, iks: dict) -> dict:
    """Update IKS mapping in state."""
    if "guna" in iks:
        state["iks"]["guna"] = iks["guna"]
    if "dominant_concepts" in iks:
        state["iks"]["dominant_concepts"] = iks["dominant_concepts"]
    if "brief_mapping" in iks:
        state["iks"]["brief_mapping"] = iks["brief_mapping"]
    return state


def update_persona(state: dict, persona: str, reason: str) -> dict:
    """Update persona and the reasoning for selection."""
    state["persona"] = persona
    state["persona_reason"] = reason
    return state


def get_conversation_history(state: dict, max_turns: int = 10) -> list:
    """Return the last N message turns for LLM context."""
    return state["messages"][-max_turns * 2:]
