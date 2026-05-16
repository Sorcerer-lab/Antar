# 🪷 Antar — Indic Wisdom Mental Wellness Guide
for demo visit @ [antar](https://antar-mental-wellness-guide.streamlit.app/)

> **"Antar"** (अन्तर) — Sanskrit for *"inner"* or *"within"*

A safety-first mental wellness chatbot grounded in **Indic Knowledge Systems (IKS)**, powered by dynamic **5Ps psychological formulation**, and delivered through **four persona-adaptive wisdom guides** — all running on a free Groq/Llama 3 backend.

---

## What Makes Antar Different

Most mental wellness chatbots apply a single Western therapeutic framework (CBT, DBT) uniformly to every user. Antar takes a different approach:

- **Clinical depth** — Every message updates a live 5Ps psychological formulation (the same structured case model used by trained counsellors), giving the system a continuously-evolving picture of the person's inner landscape.
- **Cultural grounding** — The formulation is mapped to Indic philosophical concepts (Gunas, Chitta Vritti, Dharma conflict, Ahamkara) and displayed as a contextual insight — not to route responses, but to surface a mirror of the person's state in a language rooted in their own tradition.
- **Persona-driven wisdom** — A dedicated LLM call selects the most appropriate wisdom guide (Krishna, Patanjali, Buddha, or the Upanishadic Guide) based on the psychological formulation, and that persona speaks with authentic voice, philosophy, and contextually chosen scripture citations.
- **Two-layer safety** — A keyword fast-path catches explicit crisis language instantly; a semantic LLM risk scorer catches indirect, coded, or escalating distress across the conversation history.

---

## Architecture

```
User Input
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│                      process_turn()                         │
│                    (orchestrator.py)                         │
│                                                             │
│  1. append_message()      ── add user turn to history       │
│  2. quick_risk_check()    ── keyword fast-path (no LLM)     │
│         │ HIGH? ──────────────────────── escalation_response│
│  3. detect_risk()         ── LLM semantic risk scorer       │
│         │ HIGH? ──────────────────────── escalation_response│
│  4. update_five_ps()      ── LLM → JSON → state             │
│  5. update_iks()          ── LLM → JSON → state (display)   │
│  6. update_persona()      ── LLM → JSON → state             │
│  7. generate_response()   ── LLM → plain text (persona)     │
│  8. build_citation()      ── LLM → JSON (scripture lookup)  │
│  9. append_message()      ── add assistant turn to history  │
└────────────────────────────────────────────────────────────┘
    │
    ▼
Streamlit UI (app.py)
  ├── Chat: persona response + scripture citation
  └── Sidebar: risk badge · active persona · IKS mapping · 5Ps · raw JSON
```

> **Note on Gunas:** The Guna (Sattva / Rajas / Tamas) is computed by the IKS mapping step and displayed in the sidebar as a reflective insight for the user. It does **not** influence persona selection — persona routing is driven entirely by the 5Ps formulation and the LLM persona selector.

---

## Four Wisdom Guides

| Persona | Source | Best For |
|---|---|---|
| **Krishna** | Bhagavad Gita | Dharma conflict, pressure, identity confusion, purposelessness |
| **Patanjali** | Yoga Sutras | Anxiety, overthinking, mental agitation, lack of focus |
| **Buddha** | Dhammapada / Majjhima Nikaya | Grief, sadness, attachment, existential pain |
| **Upanishadic Guide** | The Upanishads | Self-doubt, identity crisis, existential questioning, self-inquiry |

Each response includes a **dynamically selected scripture citation** — the LLM reasons about the user's specific situation and finds the most fitting verse from the persona's source text, translated into warm plain English.

---

## Module Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI, session state, chat interface, sidebar dashboard |
| `orchestrator.py` | Pipeline controller — coordinates all LLM calls and state updates |
| `prompts.py` | All prompt-builder functions (5Ps, IKS, persona selection, response, citation) |
| `risk.py` | Two-layer hybrid risk detection + escalation response |
| `state_manager.py` | Immutable-style state operations (init, update, reset, history) |
| `utils.py` | Safe JSON parsing, word-limit truncation, fallback helpers |
| `config.py` | Personas (with Arjuna parallels), risk keywords, IKS concepts, model settings |
| `test_cases.json` | 10 annotated test cases for manual or automated testing |

---

## Pipeline in Detail

### Layer 1 — Safety (Zero Latency)
Keyword scan runs before any LLM call. Explicit high-risk language (`"kill myself"`, `"want to die"`, etc.) triggers an immediate compassionate crisis escalation message with Indian helpline numbers — no pipeline steps execute.

### Layer 2 — Semantic Risk Scoring (LLM)
A focused LLM call evaluates the current message alongside the last three conversation turns, returning a structured risk assessment:
- **Risk level:** HIGH / MEDIUM / LOW
- **Confidence score:** 0.0 – 1.0
- **Signal flags:** passive ideation, hopelessness, isolation, escalation
- **Reasoning:** one-sentence explanation of the primary signal detected

Decision logic combines both layers: a MEDIUM keyword result combined with `passive_ideation + hopelessness` signals elevates to HIGH.

### Layer 3 — 5Ps Formulation (LLM → JSON)
After every message, the LLM updates all five dimensions of the clinical formulation:
- **Presenting Problem** — what is distressing the person right now
- **Predisposing Factors** — background vulnerabilities (history, personality)
- **Precipitating Factors** — recent triggers that brought on distress
- **Perpetuating Factors** — what is maintaining or worsening the problem
- **Protective Factors** — strengths, coping resources, support systems

### Layer 4 — IKS Mapping (LLM → JSON, Display Only)
Maps the current 5Ps onto Indic philosophical concepts:
- **Guna** — dominant quality of mental state (Sattva / Rajas / Tamas)
- **Dominant Concepts** — 2–3 relevant concepts from attachment, chitta vritti, dharma conflict, viveka, vairagya, ahamkara, etc.
- **Brief Mapping** — 2–3 sentences contextualising the IKS lens

This output is shown in the sidebar as a cultural mirror. It does not route persona selection.

### Layer 5 — Persona Selection (LLM → JSON)
A dedicated LLM call examines the full 5Ps formulation and selects the most appropriate wisdom guide, with a short reasoning note. Persona stability is preserved — a switch only happens when another persona would provide meaningfully better guidance.

### Layer 6 — Response + Citation (Two LLM Calls)
**Call 1 (plain text):** The selected persona speaks directly to the user — warm, authentic, never clinical. Includes one practical step and ends with an open reflective question. Capped at 300 words.

**Call 2 (JSON citation):** A separate LLM call finds the single most contextually fitting verse from the persona's source text, given the user's specific situation and the response just generated. Returns `citation_text` (plain English translation) and `citation_ref` (precise source location). Citation failure is non-fatal — the response renders without a footnote.

---

## Setup

### Prerequisites
- Python 3.11+
- A free [Groq API key](https://console.groq.com) (no credit card required)

### Installation

```bash
git clone https://github.com/Sorcerer-lab/Antar.git
cd Antar
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### Configure API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Or export it directly:

```bash
export GROQ_API_KEY="gsk_..."
```

### Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### Deploying to Streamlit Cloud

1. Push the repo to GitHub
2. Connect it at [share.streamlit.io](https://share.streamlit.io)
3. Add `GROQ_API_KEY` under **Settings → Secrets** in the Streamlit Cloud dashboard

---

## Running Test Cases

```bash
python - <<'EOF'
import json
from orchestrator import process_turn
from state_manager import initialize_state

with open("test_cases.json") as f:
    cases = json.load(f)

for case in cases:
    state = initialize_state()
    print(f"\n--- Test {case['id']}: {case['category']} ---")
    response_data, state = process_turn(state, case["input"])
    print(f"Risk:    {state['risk_level']} (expected: {case['expected_risk']})")
    print(f"Persona: {state['persona']} (expected: {case['likely_persona']})")
    print(f"Guna:    {state['iks']['guna']}")
    print(f"Response: {response_data['response_text'][:120]}...")
EOF
```

---

## Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| LLM | Llama 3.1 8B Instant via Groq Cloud (free tier) |
| Risk detection | Hybrid keyword + LLM semantic scorer |
| Persona routing | Dedicated LLM call on 5Ps formulation |
| State management | Python dict, session-scoped |
| Environment | python-dotenv |

---

## Limitations

**Not a clinical tool.** Antar is designed for early mental wellness support and self-reflection. It is not a substitute for professional mental health care and should not be used for diagnosis, treatment, or crisis intervention beyond helpline signposting.

**Keyword-only risk floor.** The risk engine uses a hybrid approach but cannot replace clinical assessment. False positives (over-sensitivity) and false negatives (missed signals) are both possible.

**LLM reliability.** JSON outputs from intermediate steps may occasionally fail to parse — fallback values are applied silently. Scripture citations are generated by the LLM and may contain approximations; always verify against authoritative sources.

**Cultural approximation.** IKS mappings and persona voices are inspired by the traditions but do not represent authoritative scholarly interpretations.

**No persistent memory.** Conversation state exists only within the current browser session. Refreshing the page resets everything.

---

## Crisis Resources (India)

| Service | Contact |
|---|---|
| iCall (TISS) | 9152987821 |
| Vandrevala Foundation (24/7) | 1860-2662-345 |
| NIMHANS | 080-46110007 |
| Emergency | 112 |

---

## Project Structure

```
Antar/
├── app.py              ← Streamlit UI entry point
├── orchestrator.py     ← Pipeline controller (8 steps per turn)
├── prompts.py          ← All LLM prompt builders (5 functions)
├── risk.py             ← Two-layer hybrid risk detection
├── state_manager.py    ← State operations (init / update / reset)
├── utils.py            ← JSON parsing, truncation, fallbacks
├── config.py           ← Personas, keywords, IKS concepts, model config
├── test_cases.json     ← 10 annotated test cases
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## License

MIT — see [LICENSE](LICENSE) for full terms.

---

*Built with Groq (Llama 3.1) · Streamlit · Indic wisdom traditions*
