
import streamlit as st

# ── Page configuration (must be first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="FinSentinel-AI | Financial Cyber Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — dark SOC theme ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #0a0e1a;
    color: #c9d1e0;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1120 0%, #111827 100%);
    border-right: 1px solid #1e2d45;
}
section[data-testid="stSidebar"] .stRadio label {
    color: #8899aa !important;
    font-size: 0.9rem;
    padding: 6px 0;
}
section[data-testid="stSidebar"] .stRadio div[data-checked="true"] label {
    color: #00d4ff !important;
    font-weight: 700;
}

/* ── Metric cards ── */
div[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 16px 20px;
}
div[data-testid="metric-container"] label {
    color: #6b7a99 !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-size: 1.9rem;
    font-weight: 700;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0057ff 0%, #00a8ff 100%);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 28px;
    font-weight: 600;
    letter-spacing: 0.04em;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.88; }

/* ── Code / rule blocks ── */
.stCodeBlock, pre {
    background: #0d1120 !important;
    border: 1px solid #1e2d45;
    border-radius: 8px;
    color: #7ee787 !important;
}

/* ── Dataframes / tables ── */
.stDataFrame { border: 1px solid #1e2d45; border-radius: 8px; }

/* ── Section headings ── */
h1, h2, h3 {
    color: #e2e8f0 !important;
    letter-spacing: -0.01em;
}

/* ── Dividers ── */
hr { border-color: #1e2d45; }

/* ── Alert banners ── */
.alert-critical {
    background: #2d0a0a; border-left: 4px solid #ff4b4b;
    border-radius: 6px; padding: 12px 16px; margin: 8px 0;
    color: #ffaaaa; font-size: 0.9rem;
}
.alert-high {
    background: #2d1a00; border-left: 4px solid #ff9933;
    border-radius: 6px; padding: 12px 16px; margin: 8px 0;
    color: #ffcc88; font-size: 0.9rem;
}
.alert-medium {
    background: #1a200a; border-left: 4px solid #c8e63b;
    border-radius: 6px; padding: 12px 16px; margin: 8px 0;
    color: #ddee88; font-size: 0.9rem;
}
.alert-low {
    background: #0a1a20; border-left: 4px solid #00d4ff;
    border-radius: 6px; padding: 12px 16px; margin: 8px 0;
    color: #88ddff; font-size: 0.9rem;
}

/* ── Status badges ── */
.badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 999px; font-size: 0.75rem; font-weight: 700;
}
.badge-critical { background:#ff4b4b22; color:#ff4b4b; border:1px solid #ff4b4b55; }
.badge-high     { background:#ff993322; color:#ff9933; border:1px solid #ff993355; }
.badge-medium   { background:#c8e63b22; color:#c8e63b; border:1px solid #c8e63b55; }
.badge-low      { background:#00d4ff22; color:#00d4ff; border:1px solid #00d4ff55; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ FinSentinel-AI")
    st.markdown("*Financial Cyber Defense Platform*")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        options=[
            "🏠  Home",
            "🔍  Fraud Detection",
            "⚠️  Risk Analysis",
            "📈  Explainability",
            "🛡️  Sigma Rules",
            "🧬  YARA Rules",
            "🚨  Alert Dashboard",
            "📊  Analytics",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("v1.0.0 · Built with FastAPI + Streamlit")
    st.caption("Model: Random Forest + XGBoost")

# ── Route to pages ───────────────────────────────────────────────────────────
if page == "🏠  Home":
    from home import render
    render()

elif page == "🔍  Fraud Detection":
    from fraud_detection import render
    render()

elif page == "⚠️  Risk Analysis":
    from risk_analysis import render
    render()

elif page == "📈  Explainability":
    from explainability import render
    render()

elif page == "🛡️  Sigma Rules":
    from sigma_rules import render
    render()

elif page == "🧬  YARA Rules":
    from yara_rules import render
    render()

elif page == "🚨  Alert Dashboard":
    from alert_dashboard import render
    render()

elif page == "📊  Analytics":
    from analytics import render
    render()
