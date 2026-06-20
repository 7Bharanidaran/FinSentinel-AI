
import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

API_BASE = "http://127.0.0.1:8000"

TYPE_MAP = {
    "CASH_IN": 0, "CASH_OUT": 1, "DEBIT": 2, "PAYMENT": 3, "TRANSFER": 4,
}

LEVEL_COLOR = {
    "Critical": "#ff4b4b",
    "High":     "#ff9933",
    "Medium":   "#c8e63b",
    "Low":      "#00d4ff",
}


def _risk_gauge(score: int, level: str) -> go.Figure:
    color = LEVEL_COLOR.get(level, "#00d4ff")
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": f"Risk Score — {level}", "font": {"color": "#c9d1e0"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#6b7a99"},
                "bar": {"color": color},
                "bgcolor": "#111827",
                "bordercolor": "#1e2d45",
                "steps": [
                    {"range": [0, 30],  "color": "#0a1a20"},
                    {"range": [30, 60], "color": "#1a200a"},
                    {"range": [60, 80], "color": "#2d1a00"},
                    {"range": [80, 100], "color": "#2d0a0a"},
                ],
            },
            number={"font": {"color": color, "size": 52}},
        )
    )
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font={"color": "#c9d1e0"},
        margin=dict(l=20, r=20, t=50, b=20),
        height=300,
    )
    return fig


def _history_chart() -> go.Figure:
    """Placeholder historical risk trend."""
    df = pd.DataFrame({
        "Transaction": [f"TXN-{1000 + i}" for i in range(10)],
        "Risk Score":  [22, 45, 78, 91, 60, 35, 88, 55, 70, 96],
        "Level":       ["Low","Medium","High","Critical","Medium",
                        "Low","Critical","Medium","High","Critical"],
    })
    color_map = {
        "Critical": "#ff4b4b", "High": "#ff9933",
        "Medium": "#c8e63b",   "Low": "#00d4ff",
    }
    fig = px.bar(
        df, x="Transaction", y="Risk Score", color="Level",
        color_discrete_map=color_map,
        title="Recent Transaction Risk Scores",
    )
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0a0e1a",
        font={"color": "#c9d1e0"},
        xaxis=dict(gridcolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45", range=[0, 100]),
        legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def render():
    st.markdown("# ⚠️ Risk Analysis")
    st.markdown(
        "Evaluate transaction risk level and receive an automated response recommendation."
    )
    st.markdown("---")

    # ── Input form ───────────────────────────────────────────────────────────
    st.markdown("#### 📋 Transaction Details")
    c1, c2 = st.columns(2)

    with c1:
        step = st.number_input("Step", min_value=1, max_value=744, value=1)
        txn_type_label = st.selectbox("Type", list(TYPE_MAP.keys()), index=4)
        txn_type = TYPE_MAP[txn_type_label]
        amount = st.number_input("Amount (USD)", min_value=0.0,
                                 value=950000.0, step=10000.0, format="%.2f")
        is_flagged = st.selectbox("System-Flagged?", ["No (0)", "Yes (1)"])
        is_flagged_val = int(is_flagged.split("(")[1].rstrip(")"))

    with c2:
        old_bal_orig = st.number_input("Sender Opening Bal.", min_value=0.0,
                                       value=1000000.0, step=10000.0, format="%.2f")
        new_bal_orig = st.number_input("Sender Closing Bal.", min_value=0.0,
                                       value=50000.0, step=10000.0, format="%.2f")
        old_bal_dest = st.number_input("Receiver Opening Bal.", min_value=0.0,
                                       value=0.0, step=10000.0, format="%.2f")
        new_bal_dest = st.number_input("Receiver Closing Bal.", min_value=0.0,
                                       value=950000.0, step=10000.0, format="%.2f")

    run = st.button("⚠️ Analyze Risk", use_container_width=False)

    # ── Results ──────────────────────────────────────────────────────────────
    if run:
        payload = {
            "step": step, "type": txn_type, "amount": amount,
            "oldbalanceOrg": old_bal_orig, "newbalanceOrig": new_bal_orig,
            "oldbalanceDest": old_bal_dest, "newbalanceDest": new_bal_dest,
            "isFlaggedFraud": is_flagged_val,
        }

        try:
            r_score = requests.post(f"{API_BASE}/risk-score", json=payload, timeout=5)
            r_score.raise_for_status()
            score_data = r_score.json()

            r_rec = requests.post(f"{API_BASE}/recommendation", json=payload, timeout=5)
            r_rec.raise_for_status()
            rec_data = r_rec.json()

        except requests.exceptions.ConnectionError:
            st.error("❌ FastAPI backend unreachable. Start it first.")
            return
        except Exception as e:
            st.error(f"❌ API error: {e}")
            return

        risk_score = score_data.get("risk_score", 0)
        risk_level = score_data.get("risk_level", "Low")
        recommendation = rec_data.get("recommendation", "N/A")
        level_color = LEVEL_COLOR.get(risk_level, "#00d4ff")

        st.markdown("---")
        st.markdown("#### 📊 Risk Assessment Results")

        # Score cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Risk Score", f"{risk_score} / 100")
        m2.metric("Risk Level", risk_level)
        m3.metric("Recommendation", recommendation)
        m4.metric("Amount", f"${amount:,.0f}")

        # Level badge + gauge
        col_badge, col_gauge = st.columns([1, 2])

        with col_badge:
            st.markdown(
                f"""
                <div style="margin-top:24px;background:#111827;border:1px solid #1e2d45;
                            border-radius:10px;padding:30px;text-align:center;">
                    <div style="font-size:0.8rem;color:#6b7a99;text-transform:uppercase;
                                letter-spacing:0.1em;margin-bottom:12px;">Risk Level</div>
                    <div style="font-size:2.5rem;font-weight:900;color:{level_color};">
                        {risk_level.upper()}
                    </div>
                    <div style="margin-top:16px;font-size:0.85rem;color:#8899aa;">
                        Action: <strong style="color:{level_color};">{recommendation}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_gauge:
            st.plotly_chart(
                _risk_gauge(risk_score, risk_level), use_container_width=True
            )

        # Risk explanation
        st.markdown("---")
        st.markdown("#### 🗂️ Risk Factor Summary")
        factors = {
            "Amount vs. Opening Balance Ratio": f"{amount / max(old_bal_orig, 1) * 100:.1f}%",
            "Transaction Type": txn_type_label,
            "System Pre-Flag": "Yes" if is_flagged_val else "No",
            "Receiver Balance Change": f"${new_bal_dest - old_bal_dest:+,.2f}",
        }
        factor_df = pd.DataFrame(
            factors.items(), columns=["Risk Factor", "Value"]
        )
        st.dataframe(factor_df, use_container_width=True, hide_index=True)

    # ── Historical chart (always shown) ──────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📈 Historical Risk Trend (Sample)")
    st.plotly_chart(_history_chart(), use_container_width=True)
