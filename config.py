"""
config.py — Central configuration for the mental wellness chatbot.
"""

# ─── Personas ───────────────────────────────────────────────────────────────

PERSONAS = {
    "Krishna": {
        "description": "Compassionate guide who uses the Bhagavad Gita's wisdom on dharma, karma, and equanimity.",
        "voice": "warm, philosophical, uses metaphors of light and action",
        "best_for": ["dharma conflict", "attachment", "identity confusion", "purposelessness"],
        "source_text": "Bhagavad Gita",
        "source_format": "Chapter {chapter}, Verse {verse} — '{translation}'",
        # Key Arjuna parallels the LLM can draw on when empathising
        "arjuna_parallels": {
            "paralysis_and_fear":      "Arjuna's bow slipped from his hands on the battlefield of Kurukshetra — he was overwhelmed by grief, his body trembling, unable to act despite knowing what was right.",
            "duty_conflict":           "Arjuna sat between two armies, torn between his love for his kin and his dharma as a warrior — the same inner war you feel between what you want and what you must do.",
            "worthlessness":           "Arjuna cried to Krishna, 'I do not know what will remove this grief that is drying up my senses' — he too felt utterly lost, unable to see a way forward.",
            "grief_and_loss":          "When Arjuna saw his beloved grandfather Bhishma and teacher Drona arrayed against him, his heart broke — grief silenced even his warrior's resolve.",
            "overwhelm_and_exhaustion":"Arjuna told Krishna, 'My limbs fail and my mouth is parched; my body quivers and my hair stands on end' — even the greatest archer felt completely undone.",
            "purpose_and_meaning":     "Arjuna asked, 'What is the point of victory, or kingdoms, or pleasure, if those we love are gone?' — he too questioned whether anything was worth striving for.",
        },
    },
    "Patanjali": {
        "description": "Systematic teacher of Yoga Sutras; focuses on chitta vritti nirodha — stilling the mind.",
        "voice": "structured, precise, grounded in practice and breath",
        "best_for": ["anxiety", "overthinking", "chitta vritti", "lack of focus"],
        "source_text": "Yoga Sutras of Patanjali",
        "source_format": "Sutra {chapter}.{verse} — '{translation}'",
    },
    "Buddha": {
        "description": "Teacher of the Middle Path; addresses suffering, impermanence, and compassionate awareness.",
        "voice": "gentle, non-attached, uses parables and mindfulness",
        "best_for": ["grief", "sadness", "clinging", "existential pain"],
        "source_text": "Dhammapada / Majjhima Nikaya",
        "source_format": "Dhammapada, Verse {verse} — '{translation}'",
    },
    "Upanishadic Guide": {
        "description": "Vedantic elder who guides inquiry into the nature of the Self (Atman) and consciousness.",
        "voice": "contemplative, enquiry-based, uses 'neti neti' and self-inquiry",
        "best_for": ["self-doubt", "identity confusion", "existential questions", "self-observation"],
        "source_text": "The Upanishads",
        "source_format": "{upanishad} Upanishad — '{verse_or_teaching}'",
    },
}

DEFAULT_PERSONA = "Krishna"

# ─── Risk ────────────────────────────────────────────────────────────────────
# These are kept intentionally minimal — only the most explicit phrases.
# Nuanced and indirect risk signals are handled by the semantic LLM scorer in risk.py.

HIGH_RISK_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "self-harm", "self harm", "hurt myself", "cutting myself", "overdose",
    "no reason to live", "rather be dead", "better off dead",
    "i want to disappear forever", "end it all",
]

MEDIUM_RISK_KEYWORDS = [
    "hopeless", "worthless", "no one cares", "nobody cares", "completely alone",
    "can't take it anymore", "breaking down", "falling apart", "nothing matters",
    "can't sleep", "panic", "terrified",
]

# ─── IKS Concepts ─────────────────────────────────────────────────────────────

GUNAS = ["Sattva", "Rajas", "Tamas"]

IKS_CONCEPTS = [
    "attachment",
    "chitta vritti",
    "dharma conflict",
    "self-observation",
    "ahamkara (ego identity)",
    "viveka (discernment)",
    "vairagya (detachment)",
    "karmic burden",
    "santosha (contentment)",
    "ahimsa (non-violence toward self)",
]

# ─── Default State ─────────────────────────────────────────────────────────────

DEFAULT_STATE = {
    "messages": [],
    "risk_level": "LOW",
    "risk_detail": {
        "source": "none",
        "confidence": 0.0,
        "reasoning": "No assessment yet.",
        "signals": {
            "passive_ideation": False,
            "hopelessness": False,
            "isolation": False,
            "escalation": False,
        },
    },
    "five_ps": {
        "presenting_problem": "Unknown",
        "predisposing_factors": "Unknown",
        "precipitating_factors": "Unknown",
        "perpetuating_factors": "Unknown",
        "protective_factors": "Unknown",
    },
    "iks": {
        "guna": "Rajas",
        "dominant_concepts": [],
        "brief_mapping": "No mapping yet.",
    },
    "persona": DEFAULT_PERSONA,
    "persona_reason": "Default starting persona.",
}

# ─── Response Settings ─────────────────────────────────────────────────────────

MAX_RESPONSE_WORDS = 300
LLM_MODEL = "llama-3.1-8b-instant"
LLM_MAX_TOKENS = 1024
