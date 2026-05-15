"""
app.py — Streamlit UI for the Safety-aware Mental Wellness Chatbot.
"""
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import streamlit as st
import json
from orchestrator import process_turn
from state_manager import initialize_state, reset_state
from utils import format_risk_badge



# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Antar — Mental Wellness Guide",
    page_icon="🪷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;1,300&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main-title {
    font-family: 'Crimson Pro', serif;
    font-size: 2.2rem;
    font-weight: 300;
    color: #dceedd;
    letter-spacing: 0.02em;
    margin-bottom: 0.1rem;
}

.subtitle {
    font-size: 0.85rem;
    color: pink;
    font-style: italic;
    margin-bottom: 1.5rem;
}

.persona-badge {
    background: linear-gradient(135deg, #f5ede4 0%, #ede0d4 100%);
    border-left: 3px solid #c4956a;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin: 8px 0;
    font-size: 0.88rem;
    color: #3d2b1f;
}

.state-block {
     background: rgba(226, 240, 217, 0.5);
    border: 1px solid #e8ddd4;
    border-radius: 8px;
    padding: 12px;
    margin: 6px 0;
    font-size: 0.80rem;
    color: #4a3728;
}

.risk-high { color: #c0392b; font-weight: 600; }
.risk-medium { color: #d68910; font-weight: 600; }
.risk-low { color: #1e8449; font-weight: 600; }

.chat-user { background: #f0ebe5; }
.chat-assistant { background: #fdfaf7; }

div[data-testid="stChatMessage"] {
    border-radius: 12px;
    margin-bottom: 6px;
}

.stButton > button {
    background: #c4956a;
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    padding: 6px 16px;
    cursor: pointer;
    transition: background 0.2s;
}
.stButton > button:hover { background: #a87850; }

.citation-block {
    font-family: 'Crimson Pro', serif;
    font-size: 0.82rem;
    color: #9b8068;
    font-style: italic;
    border-left: 2px solid #d4b896;
    padding: 4px 10px;
    margin-top: 8px;
    line-height: 1.5;
}

.citation-ref {
    font-size: 0.75rem;
    color: #b09070;
    font-style: normal;
    font-family: 'DM Sans', sans-serif;
    margin-top: 2px;
}

section[data-testid="stSidebar"] {
    background: #7A8F7B;
    border-right: 1px solid #e8ddd4;
}

.sidebar-section-title {
    font-family: 'Crimson Pro', serif;
    font-size: 1.0rem;
    font-weight: 400;
    color: #3d2b1f;
    border-bottom: 1px solid #e8ddd4;
    padding-bottom: 4px;
    margin: 14px 0 6px 0;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ───────────────────────────────────────────────────────

if "chat_state" not in st.session_state:
    st.session_state.chat_state = initialize_state()

if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

if "is_loading" not in st.session_state:
    st.session_state.is_loading = False


# ─── Header ───────────────────────────────────────────────────────────────────

col_title, col_reset = st.columns([5, 1])
with col_title:
    st.markdown('<div class="main-title">🪷 Antar</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">A safety-aware mental wellness guide rooted in Indic wisdom</div>',
        unsafe_allow_html=True,
    )
with col_reset:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺ Reset", help="Start a new conversation"):
        st.session_state.chat_state = reset_state()
        st.session_state.display_messages = []
        st.rerun()

st.divider()


# ─── Sidebar ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 🧭 Session Dashboard")

    state = st.session_state.chat_state
    risk = state["risk_level"]
    risk_class = f"risk-{risk.lower()}"

    # Risk Level
    st.markdown('<div class="sidebar-section-title">Risk Level</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="persona-badge"><span class="{risk_class}">{format_risk_badge(risk)}</span></div>',
        unsafe_allow_html=True,
    )
    risk_detail = state.get("risk_detail", {})
    if risk_detail.get("reasoning") and risk_detail["reasoning"] != "No assessment yet.":
        with st.expander("Risk reasoning", expanded=False):
            st.caption(f"**Source:** {risk_detail.get('source', '—').capitalize()}")
            st.caption(f"**Confidence:** {risk_detail.get('confidence', 0):.0%}")
            st.write(risk_detail.get("reasoning", ""))
            signals = risk_detail.get("signals", {})
            active = [k.replace("_", " ").title() for k, v in signals.items() if v]
            if active:
                st.caption("**Signals detected:** " + ", ".join(active))

    # Persona
    st.markdown('<div class="sidebar-section-title">Active Persona</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="persona-badge">🧘 <strong>{state["persona"]}</strong></div>',
        unsafe_allow_html=True,
    )
    if state["persona_reason"] and state["persona_reason"] != "Default starting persona.":
        st.markdown(
            f'<div class="state-block"><em>{state["persona_reason"]}</em></div>',
            unsafe_allow_html=True,
        )

    # IKS Mapping
    st.markdown('<div class="sidebar-section-title">Indic Knowledge Mapping</div>', unsafe_allow_html=True)
    iks = state["iks"]
    st.markdown(
        f"""<div class="state-block">
        <strong>Guna:</strong> {iks['guna']}<br>
        <strong>Concepts:</strong> {", ".join(iks['dominant_concepts']) if iks['dominant_concepts'] else "—"}<br>
        <strong>Mapping:</strong> {iks['brief_mapping']}
        </div>""",
        unsafe_allow_html=True,
    )

    # 5Ps
    st.markdown('<div class="sidebar-section-title">5Ps Formulation</div>', unsafe_allow_html=True)
    five_ps = state["five_ps"]
    five_ps_labels = {
        "presenting_problem": "Presenting Problem",
        "predisposing_factors": "Predisposing Factors",
        "precipitating_factors": "Precipitating Factors",
        "perpetuating_factors": "Perpetuating Factors",
        "protective_factors": "Protective Factors",
    }
    for key, label in five_ps_labels.items():
        val = five_ps.get(key, "Unknown")
        if val and val != "Unknown":
            with st.expander(label, expanded=False):
                st.write(val)
        else:
            st.markdown(f'<div class="state-block"><strong>{label}:</strong> —</div>', unsafe_allow_html=True)

    # Raw JSON toggle
    with st.expander("🔍 Raw State (JSON)", expanded=False):
        display_state = {k: v for k, v in state.items() if k != "messages"}
        st.json(display_state)

    st.markdown("---")
    st.caption("⚠️ This is not a substitute for professional mental health care.")


# ─── Chat Interface ───────────────────────────────────────────────────────────

# Render previous messages
for msg in st.session_state.display_messages:
    with st.chat_message(msg["role"], avatar="🧘" if msg["role"] == "assistant" else "🙂"):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("citation_text"):
            ref_line = f'<div class="citation-ref">— {msg["citation_ref"]}</div>' if msg.get("citation_ref") else ""
            st.markdown(
                f'''<div class="citation-block">{msg["citation_text"]}{ref_line}</div>''',
                unsafe_allow_html=True,
            )

# Welcome message on first load
if not st.session_state.display_messages:
    with st.chat_message("assistant", avatar="🧘"):
        welcome = (
            "Namaste 🙏 I am here with you. This is a safe space to share whatever "
            "is weighing on your heart or mind. What would you like to explore today?"
        )
        st.markdown(welcome)

# Input box
user_input = st.chat_input(
    "Share what's on your mind…",
    disabled=st.session_state.is_loading,
)

if user_input and user_input.strip():
    # Show user message immediately
    st.session_state.display_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🙂"):
        st.markdown(user_input)

    # Process through pipeline
    with st.chat_message("assistant", avatar="🧘"):
        with st.spinner("Reflecting…"):
            try:
                response_data, updated_state = process_turn(
                    state=st.session_state.chat_state,
                    user_message=user_input,
                )
                st.session_state.chat_state = updated_state
                # response_data is a dict for normal turns, a plain string for crisis escalation
                response_text = response_data.get("response_text", "")
                citation_text = response_data.get("citation_text", "")
                citation_ref  = response_data.get("citation_ref", "")
            except Exception as e:
                response_text  = (
                    "I'm here with you. Something went wrong on my end — "
                    "could you share that again? I'm listening."
                )
                citation_text  = ""
                citation_ref   = ""
                import traceback
                print(f"[orchestrator error] {traceback.format_exc()}")

        st.markdown(response_text)
        if citation_text:
            ref_line = f'<div class="citation-ref">— {citation_ref}</div>' if citation_ref else ""
            st.markdown(
                f'''<div class="citation-block">{citation_text}{ref_line}</div>''',
                unsafe_allow_html=True,
            )

    display_entry = {"role": "assistant", "content": response_text}
    if citation_text:
        display_entry["citation_text"] = citation_text
        display_entry["citation_ref"]  = citation_ref
    st.session_state.display_messages.append(display_entry)
    st.rerun()
