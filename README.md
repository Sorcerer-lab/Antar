# Antar
A spiritual mental wellness guide based on bhagwad gita , yoga sutras , dhamapada, upanishad teachings
# 🪷 Antar — Safety-Aware Mental Wellness Chatbot

> *"Antar" (अन्तर) — Sanskrit for "inner" or "within".*

A modular, safety-aware mental wellness chatbot grounded in **Indic Knowledge Systems (IKS)**,
powered by dynamic **5Ps psychological formulation**, and delivered through persona-adaptive
response generation using Claude (Anthropic).

---

## Architecture Overview

```
User Input
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│                     process_turn()                        │
│                    (orchestrator.py)                      │
│                                                          │
│  1. append_message() ──────────────────────────────────  │
│  2. detect_risk() ─────────── HIGH? → escalation_response│
│  3. update_five_ps() ──────── LLM → JSON → state         │
│  4. update_iks() ──────────── LLM → JSON → state         │
│  5. update_persona() ──────── LLM → JSON → state         │
│  6. generate_response() ───── LLM → text → truncate      │
│  7. append_message() ──────────────────────────────────  │
└──────────────────────────────────────────────────────────┘
    │
    ▼
Streamlit UI (app.py)
  ├── Chat messages
  └── Sidebar: risk | persona | IKS | 5Ps | raw JSON
```

### Module Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | Streamlit UI, session state, chat interface, sidebar |
| `orchestrator.py` | Pipeline controller, LLM calls, step coordination |
| `prompts.py` | All LLM prompt builders (5Ps, IKS, persona, response) |
| `risk.py` | Keyword-based risk detection, escalation response |
| `state_manager.py` | Immutable state operations (init, update, reset) |
| `utils.py` | Safe JSON parsing, truncation, fallback helpers |
| `config.py` | Personas, keywords, defaults, model settings |
| `test_cases.json` | 10 annotated test cases for manual/automated testing |

---

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- An **Anthropic API key** ([get one here](https://console.anthropic.com/))

### 2. Clone / copy the project
```bash
mkdir antar && cd antar
# copy all project files here
```

### 3. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Set your API key
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
```

Or export it directly:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 6. Run the app
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Features

### 🔒 Safety-First Design
- Keyword-based HIGH/MEDIUM/LOW risk classification on every message
- HIGH risk (suicidal ideation, self-harm) **immediately bypasses all pipelines**
  and returns a compassionate crisis escalation message with helpline numbers
- No persona or psychological analysis is performed on HIGH-risk inputs

### 🧠 Dynamic 5Ps Formulation
After every user message, the LLM updates all five dimensions:
- **Presenting Problem** — What is distressing the person right now
- **Predisposing Factors** — Background vulnerabilities
- **Precipitating Factors** — Recent triggers
- **Perpetuating Factors** — What is maintaining the distress
- **Protective Factors** — Strengths and resources

### 🪷 Indic Knowledge Mapping
Maps the formulation to:
- **Guna** (Sattva / Rajas / Tamas) — Quality of mental state
- **Dominant Concepts** — From attachment, chitta vritti, dharma conflict, viveka, etc.
- **Brief Mapping** — Explanation of how IKS concepts apply

### 🎭 Persona-Adaptive Responses
Four Indic wisdom personas, auto-selected each turn:
| Persona | Best For |
|---|---|
| **Krishna** | Dharma conflict, identity, purpose, anger |
| **Patanjali** | Anxiety, overthinking, mental agitation |
| **Buddha** | Grief, sadness, attachment, impermanence |
| **Upanishadic Guide** | Existential questions, self-inquiry, emptiness |

### 📊 Live Sidebar Dashboard
- Risk level badge (🟢/🟡/🔴)
- Current persona + reasoning
- IKS guna + concepts + mapping
- 5Ps formulation (expandable)
- Raw JSON state viewer

---

## How to Run Test Cases

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
    response, state = process_turn(state, case["input"])
    print(f"Risk: {state['risk_level']} (expected: {case['expected_risk']})")
    print(f"Persona: {state['persona']} (expected: {case['likely_persona']})")
    print(f"Guna: {state['iks']['guna']}")
    print(f"Response: {response[:120]}...")
EOF
```

---

## Limitations

1. **Not a clinical tool** — This chatbot is not a replacement for professional mental health care.
   It should not be used for diagnosis, treatment, or crisis intervention beyond signposting.

2. **Keyword-only risk detection** — The risk engine uses pattern matching, not clinical assessment.
   It can produce false positives (over-sensitive) and false negatives (missed signals).

3. **LLM reliability** — JSON outputs from intermediate steps may occasionally fail to parse;
   fallback values are applied silently in these cases.

4. **Cultural context** — IKS mappings and persona voices are approximate; they are inspired by
   the traditions but do not represent authoritative scholarly interpretations.

5. **No persistent memory** — Conversation state exists only within the current browser session.
   Refreshing the page resets everything.

6. **Response length** — Responses are capped at ~100 words for safety and accessibility.
   Complex situations may warrant more nuanced engagement than this allows.

---

## Folder Structure

```
project/
├── app.py              ← Streamlit UI entry point
├── orchestrator.py     ← Pipeline controller
├── prompts.py          ← All LLM prompt builders
├── risk.py             ← Risk detection + escalation
├── state_manager.py    ← State operations
├── utils.py            ← JSON helpers + utilities
├── config.py           ← Central configuration
├── test_cases.json     ← 10 annotated test cases
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## Crisis Resources (India)

| Service | Contact |
|---|---|
| iCall (TISS) | 9152987821 |
| Vandrevala Foundation (24/7) | 1860-2662-345 |
| NIMHANS | 080-46110007 |
| Emergency | 112 |

---

*Built with Claude (Anthropic) · Streamlit · Indic wisdom traditions*

