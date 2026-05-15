"""
orchestrator.py — Main pipeline controller.
Orchestrates: risk detection → 5Ps update → IKS mapping → persona selection → response generation.
"""

import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st


# Load .env file first, before anything else
load_dotenv()

from config import LLM_MODEL, LLM_MAX_TOKENS, MAX_RESPONSE_WORDS
from prompts import (
    build_fiveps_update_prompt,
    build_iks_prompt,
    build_persona_prompt,
    build_response_prompt,
    build_citation_prompt,
)
from risk import detect_risk, quick_risk_check, escalation_response
import state_manager as sm
from utils import (
    fallback_five_ps,
    fallback_iks,
    fallback_persona,
    fallback_response,
    parse_response_json,
    safe_json_load,
    truncate_to_word_limit,
)

# Initialise Groq client
api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
_client = Groq(api_key=api_key)


# ─── Core LLM Call ────────────────────────────────────────────────────────────

def call_llm(prompt: str) -> str:
    """
    Send a prompt to Groq (Llama 3) and return the raw text response.
    """
    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=LLM_MAX_TOKENS,
    )
    return response.choices[0].message.content


# ─── Pipeline Steps ───────────────────────────────────────────────────────────

def update_five_ps(state: dict, user_message: str) -> dict:
    history = sm.get_conversation_history(state)
    prompt = build_fiveps_update_prompt(
        user_message=user_message,
        previous_five_ps=state["five_ps"],
        conversation_history=history,
    )
    try:
        raw = call_llm(prompt)
        parsed = safe_json_load(raw, fallback=fallback_five_ps())
        state = sm.update_five_ps(state, parsed)
    except Exception as e:
        print(f"[update_five_ps] fallback due to: {e}")
    return state


def update_iks(state: dict) -> dict:
    prompt = build_iks_prompt(five_ps=state["five_ps"])
    try:
        raw = call_llm(prompt)
        parsed = safe_json_load(raw, fallback=fallback_iks())
        state = sm.update_iks(state, parsed)
    except Exception as e:
        print(f"[update_iks] fallback due to: {e}")
    return state


def update_persona(state: dict) -> dict:
    prompt = build_persona_prompt(
        five_ps=state["five_ps"],
        iks=state["iks"],
        current_persona=state["persona"],
    )
    try:
        raw = call_llm(prompt)
        parsed = safe_json_load(raw, fallback=fallback_persona(state["persona"]))
        persona = parsed.get("persona", state["persona"])
        reason = parsed.get("reason", state["persona_reason"])
        state = sm.update_persona(state, persona, reason)
    except Exception as e:
        print(f"[update_persona] fallback due to: {e}")
    return state


def generate_response(state: dict, user_message: str) -> dict:
    """
    Two separate LLM calls:
      Call 1 — Plain text response from the persona. No JSON, no formatting.
               This eliminates the raw-JSON-in-chat bug for all personas.
      Call 2 — Dynamic citation lookup. Given the user context + response just
               generated, find the most fitting verse from the persona's
               source text. Returns JSON independently of the response.

    Returns: { response_text, citation_text, citation_ref }
    """
    history = sm.get_conversation_history(state)
    persona = state["persona"]
    five_ps = state["five_ps"]
    iks     = state["iks"]

    # ── Call 1: plain text persona response ──────────────────────────────────
    response_text = ""
    try:
        response_prompt = build_response_prompt(
            user_message=user_message,
            persona=persona,
            five_ps=five_ps,
            iks=iks,
            conversation_history=history,
        )
        raw_response = call_llm(response_prompt)
        # Plain text — just truncate, no JSON parsing needed
        response_text = truncate_to_word_limit(raw_response.strip(), MAX_RESPONSE_WORDS)
    except Exception as e:
        print(f"[generate_response] response call failed: {e}")
        response_text = fallback_response()["response_text"]

    # ── Call 2: dynamic citation lookup ──────────────────────────────────────
    citation_text = ""
    citation_ref  = ""
    try:
        citation_prompt = build_citation_prompt(
            user_message=user_message,
            response_text=response_text,
            persona=persona,
            five_ps=five_ps,
            iks=iks,
        )
        raw_citation = call_llm(citation_prompt)
        parsed = safe_json_load(raw_citation, fallback={})
        citation_text = parsed.get("citation_text", "")
        citation_ref  = parsed.get("citation_ref", "")
    except Exception as e:
        print(f"[generate_response] citation call failed (non-fatal): {e}")
        # Citation failure is non-fatal — response still shows without footnote

    return {
        "response_text": response_text,
        "citation_text": citation_text,
        "citation_ref":  citation_ref,
    }


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def process_turn(state: dict, user_message: str) -> tuple:
    """
    Full pipeline for a single conversation turn.
    Flow:
        1. Append user message to history
        2. Keyword fast-path  →  if explicit HIGH → escalate immediately (no LLM)
        3. Semantic risk LLM  →  context-aware assessment, returns rich result dict
        4. If HIGH (semantic or hybrid) → escalate
        5. Update 5Ps      (LLM → JSON → state)
        6. Update IKS      (LLM → JSON → state)
        7. Update persona  (LLM → JSON → state)
        8. Generate final response  (LLM → text)
        9. Append assistant response to history
       10. Return (response_text, updated_state)
    """
    state = sm.append_message(state, role="user", content=user_message)

    # Layer 1: keyword fast-path — zero latency, no LLM call needed
    if quick_risk_check(user_message):
        state = sm.update_risk(state, "HIGH", {
            "source": "keyword",
            "confidence": 1.0,
            "reasoning": "Explicit high-risk language detected in message.",
            "signals": {"passive_ideation": False, "hopelessness": False,
                        "isolation": False, "escalation": False},
        })
        crisis_text = escalation_response()
        state = sm.append_message(state, role="assistant", content=crisis_text)
        return {"response_text": crisis_text, "citation_text": "", "citation_ref": ""}, state

    # Layer 2: semantic LLM risk assessment (catches indirect / coded distress)
    history = sm.get_conversation_history(state)
    risk_result = detect_risk(user_message, history, call_llm)
    state = sm.update_risk(state, risk_result["risk_level"], risk_result)

    if risk_result["risk_level"] == "HIGH":
        crisis_text = escalation_response()
        state = sm.append_message(state, role="assistant", content=crisis_text)
        return {"response_text": crisis_text, "citation_text": "", "citation_ref": ""}, state

    state = update_five_ps(state, user_message)
    state = update_iks(state)
    state = update_persona(state)
    response_data = generate_response(state, user_message)
    response_text = response_data["response_text"]
    state = sm.append_message(state, role="assistant", content=response_text)

    return response_data, state
