

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


def _status_indicator(label: str, ok: bool) -> str:
    dot = "🟢" if ok else "🔴"
    return f"{dot} &nbsp; {label}"


def render():
    # ── Hero header ──────────────────────────────────────────────────────────
    st.markdown("# 🛡️ FinSentinel-AI")
    st.markdown(
        "### AI-Powered Financial Cyber Defense Platform"
    )
    st.markdown(
        "*Real-time fraud detection · Risk scoring · Threat intelligence · "
        "Automated rule generation*"
    )
    st.markdown("---")

    # ── KPI strip ────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Transactions Analyzed", "1,24,317", "+2.4K today")
    with col2:
        st.metric("Fraud Detected", "3,821", "+14 today")
    with col3:
        st.metric("Avg Risk Score", "42 / 100", "-3 vs yesterday")
    with col4:
        st.metric("Open Alerts", "27", "+5 today")

    st.markdown("---")

    # ── System status + gauge ────────────────────────────────────────────────
    left, right = st.columns([1, 1])

    with left:
        st.markdown("#### 🖥️ System Status")
        for label, status in [
            ("FastAPI Backend", True),
            ("Random Forest Model", True),
            ("XGBoost Model", True),
            ("SHAP Engine", True),
            ("Sigma Rule Generator", True),
            ("YARA Rule Generator", True),
            ("Alert Engine", True),
        ]:
            st.markdown(
                _status_indicator(label, status),
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("#### 🎯 Threat Level Gauge")

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=68,
                title={"text": "Current Threat Index", "font": {"color": "#c9d1e0"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#6b7a99"},
                    "bar": {"color": "#00d4ff"},
                    "bgcolor": "#111827",
                    "bordercolor": "#1e2d45",
                    "steps": [
                        {"range": [0, 30],  "color": "#0a1a20"},
                        {"range": [30, 60], "color": "#1a200a"},
                        {"range": [60, 80], "color": "#2d1a00"},
                        {"range": [80, 100], "color": "#2d0a0a"},
                    ],
                    "threshold": {
                        "line": {"color": "#ff4b4b", "width": 4},
                        "thickness": 0.8,
                        "value": 85,
                    },
                },
                number={"font": {"color": "#00d4ff", "size": 48}},
            )
        )
        fig.update_layout(
            paper_bgcolor="#111827",
            plot_bgcolor="#111827",
            font={"color": "#c9d1e0"},
            margin=dict(l=20, r=20, t=40, b=20),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── Feature cards ────────────────────────────────────────────────────────
    st.markdown("#### 🚀 Platform Capabilities")

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🔍", "Fraud Detection",
         "ML-powered transaction screening with Random Forest & XGBoost ensemble."),
        ("⚠️", "Risk Analysis",
         "Dynamic risk scoring from 0–100 with Critical / High / Medium / Low tiers."),
        ("📈", "SHAP Explainability",
         "Feature-level explanations so every decision is auditable and transparent."),
        ("🛡️", "Sigma & YARA Rules",
         "Auto-generated detection rules ready to deploy in any SIEM or endpoint tool."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f"""
                <div style="background:#111827;border:1px solid #1e2d45;
                            border-radius:10px;padding:20px;height:160px;">
                    <div style="font-size:2rem;">{icon}</div>
                    <div style="color:#e2e8f0;font-weight:700;margin:8px 0 6px;">{title}</div>
                    <div style="color:#6b7a99;font-size:0.82rem;line-height:1.5;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.caption(
        f"Last refreshed: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}  ·  "
        "FinSentinel-AI v1.0.0"
    )
