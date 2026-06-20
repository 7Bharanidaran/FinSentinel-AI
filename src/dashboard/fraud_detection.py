"""
fraud_detection.py — FinSentinel-AI Fraud Detection Page
Accepts transaction input, calls FastAPI /predict, and displays results.
"""

import streamlit as st
import requests
import plotly.graph_objects as go

# FastAPI base URL (update if deployed remotely)
API_BASE = "http://127.0.0.1:8000"

# ── Transaction type mapping (PaySim dataset encoding) ───────────────────────
TYPE_MAP = {
    "CASH_IN":   0,
    "CASH_OUT":  1,
    "DEBIT":     2,
    "PAYMENT":   3,
    "TRANSFER":  4,
}


def _fraud_gauge(probability: float) -> go.Figure:
    """Render a semi-circular gauge for fraud probability."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=round(probability * 100, 2),
            title={"text": "Fraud Probability (%)", "font": {"color": "#c9d1e0"}},
            delta={"reference": 50, "increasing": {"color": "#ff4b4b"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#6b7a99"},
                "bar": {"color": "#ff4b4b" if probability > 0.5 else "#00d4ff"},
                "bgcolor": "#111827",
                "bordercolor": "#1e2d45",
                "steps": [
                    {"range": [0, 30],  "color": "#0a1a20"},
                    {"range": [30, 60], "color": "#1a200a"},
                    {"range": [60, 85], "color": "#2d1a00"},
                    {"range": [85, 100], "color": "#2d0a0a"},
                ],
                "threshold": {
                    "line": {"color": "#ff4b4b", "width": 4},
                    "thickness": 0.8,
                    "value": 80,
                },
            },
            number={"suffix": "%", "font": {"color": "#00d4ff", "size": 48}},
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


def render():
    st.markdown("# 🔍 Fraud Detection")
    st.markdown("Enter transaction details to run real-time fraud screening.")
    st.markdown("---")

    # ── Input form ───────────────────────────────────────────────────────────
    st.markdown("#### 📋 Transaction Input")

    col1, col2 = st.columns(2)

    with col1:
        step = st.number_input(
            "Step (Time Unit)", min_value=1, max_value=744, value=1,
            help="1 step = 1 hour. Max 744 steps (31 days).",
        )
        txn_type_label = st.selectbox(
            "Transaction Type", list(TYPE_MAP.keys()), index=3
        )
        txn_type = TYPE_MAP[txn_type_label]
        amount = st.number_input(
            "Amount (USD)", min_value=0.0, value=100000.0, step=1000.0,
            format="%.2f",
        )
        is_flagged = st.selectbox(
            "System-Flagged Fraud?", ["No (0)", "Yes (1)"], index=0
        )
        is_flagged_val = int(is_flagged.split("(")[1].rstrip(")"))

    with col2:
        old_balance_orig = st.number_input(
            "Sender — Opening Balance", min_value=0.0, value=200000.0,
            step=1000.0, format="%.2f",
        )
        new_balance_orig = st.number_input(
            "Sender — Closing Balance", min_value=0.0, value=100000.0,
            step=1000.0, format="%.2f",
        )
        old_balance_dest = st.number_input(
            "Receiver — Opening Balance", min_value=0.0, value=0.0,
            step=1000.0, format="%.2f",
        )
        new_balance_dest = st.number_input(
            "Receiver — Closing Balance", min_value=0.0, value=100000.0,
            step=1000.0, format="%.2f",
        )

    st.markdown("")
    run = st.button("🔍 Run Fraud Screening", use_container_width=False)

    # ── API call & results ───────────────────────────────────────────────────
    if run:
        payload = {
            "step": step,
            "type": txn_type,
            "amount": amount,
            "oldbalanceOrg": old_balance_orig,
            "newbalanceOrig": new_balance_orig,
            "oldbalanceDest": old_balance_dest,
            "newbalanceDest": new_balance_dest,
            "isFlaggedFraud": is_flagged_val,
        }

        try:
            resp = requests.post(f"{API_BASE}/predict", json=payload, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            fraud_prob = data.get("fraud_probability", 0.0)

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Cannot reach FastAPI backend. "
                "Make sure `uvicorn main:app --reload` is running on port 8000."
            )
            return
        except Exception as e:
            st.error(f"❌ API error: {e}")
            return

        st.markdown("---")
        st.markdown("#### 📊 Detection Results")

        # Verdict banner
        verdict = "🚨 FRAUDULENT" if fraud_prob > 0.5 else "✅ LEGITIMATE"
        banner_color = "#2d0a0a" if fraud_prob > 0.5 else "#0a1a20"
        text_color   = "#ff4b4b" if fraud_prob > 0.5 else "#00d4ff"

        st.markdown(
            f"""
            <div style="background:{banner_color};border-radius:10px;
                        padding:18px 24px;margin-bottom:16px;
                        text-align:center;font-size:1.4rem;
                        font-weight:700;color:{text_color};">
                {verdict}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Metrics + gauge
        m1, m2, m3 = st.columns(3)
        m1.metric("Fraud Probability", f"{fraud_prob * 100:.1f}%")
        m2.metric("Transaction Amount", f"${amount:,.2f}")
        m3.metric("Type", txn_type_label)

        st.plotly_chart(_fraud_gauge(fraud_prob), use_container_width=True)

        # Raw payload echo
        with st.expander("📦 Raw API Payload"):
            st.json(payload)

        with st.expander("📩 Raw API Response"):
            st.json(data)
