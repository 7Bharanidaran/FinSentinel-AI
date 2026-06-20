

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random

API_BASE = "http://127.0.0.1:8000"

TYPE_MAP = {
    "CASH_IN": 0, "CASH_OUT": 1, "DEBIT": 2, "PAYMENT": 3, "TRANSFER": 4,
}

SEVERITY_COLOR = {
    "Critical": "#ff4b4b", "High": "#ff9933",
    "Medium": "#c8e63b",   "Low": "#00d4ff",
}

# ── Simulated alert feed (in production, fetch from DB/SIEM) ─────────────────
def _generate_sample_alerts(n: int = 15) -> pd.DataFrame:
    random.seed(42)
    severities = ["Critical", "High", "Medium", "Low"]
    weights    = [0.2, 0.35, 0.3, 0.15]
    statuses   = ["Open", "In Progress", "Closed"]
    types      = list(TYPE_MAP.keys())

    rows = []
    base_time = datetime.now() - timedelta(hours=n)
    for i in range(n):
        sev = random.choices(severities, weights=weights)[0]
        rows.append({
            "Alert ID":   f"ALT-{1001 + i}",
            "Severity":   sev,
            "Status":     random.choices(statuses, weights=[0.5, 0.3, 0.2])[0],
            "Type":       random.choice(types),
            "Amount":     round(random.uniform(10_000, 1_000_000), 2),
            "Risk Score": random.randint(
                {"Critical": 85, "High": 65, "Medium": 40, "Low": 10}[sev],
                100,
            ),
            "Timestamp":  (base_time + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M"),
            "Action":     {
                "Critical": "Block Transaction",
                "High":     "Flag for Review",
                "Medium":   "Monitor Account",
                "Low":      "Log and Continue",
            }[sev],
        })
    return pd.DataFrame(rows)


def _severity_donut(df: pd.DataFrame) -> px.pie:
    counts = df["Severity"].value_counts().reset_index()
    counts.columns = ["Severity", "Count"]
    fig = px.pie(
        counts, names="Severity", values="Count", hole=0.55,
        color="Severity",
        color_discrete_map=SEVERITY_COLOR,
        title="Alert Severity Distribution",
    )
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font={"color": "#c9d1e0"},
        legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=300,
    )
    return fig


def _timeline_chart(df: pd.DataFrame) -> px.scatter:
    fig = px.scatter(
        df, x="Timestamp", y="Risk Score", color="Severity",
        size="Amount", size_max=20,
        color_discrete_map=SEVERITY_COLOR,
        title="Alert Timeline — Risk Score vs Time",
        hover_data=["Alert ID", "Type", "Action"],
    )
    fig.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0a0e1a",
        font={"color": "#c9d1e0"},
        xaxis=dict(gridcolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45", range=[0, 105]),
        legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=340,
    )
    return fig


def render():
    st.markdown("# 🚨 Alert Dashboard")
    st.markdown(
        "Real-time security alerts from FinSentinel-AI detection engine. "
        "Generate new alerts, triage existing ones, and track resolution status."
    )
    st.markdown("---")

    # ── KPI strip ────────────────────────────────────────────────────────────
    sample_df = _generate_sample_alerts(15)
    open_alerts    = len(sample_df[sample_df["Status"] == "Open"])
    critical_count = len(sample_df[sample_df["Severity"] == "Critical"])
    high_count     = len(sample_df[sample_df["Severity"] == "High"])
    avg_risk       = int(sample_df["Risk Score"].mean())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Alerts", len(sample_df), "+3 today")
    m2.metric("Open", open_alerts, f"+{open_alerts // 2} unresolved")
    m3.metric("Critical", critical_count, "Immediate action")
    m4.metric("Avg Risk Score", avg_risk)

    st.markdown("---")

    # ── Generate new alert ────────────────────────────────────────────────────
    st.markdown("#### ⚡ Generate New Alert")
    with st.expander("Click to expand — run the alert engine on a transaction"):
        c1, c2 = st.columns(2)

        with c1:
            step        = st.number_input("Step", min_value=1, value=1, key="alt_step")
            txn_lbl     = st.selectbox("Type", list(TYPE_MAP.keys()),
                                       index=4, key="alt_type")
            txn_type    = TYPE_MAP[txn_lbl]
            amount      = st.number_input("Amount", min_value=0.0,
                                          value=950000.0, key="alt_amt")
            is_flag_str = st.selectbox("System-Flagged?",
                                       ["No (0)", "Yes (1)"], key="alt_flag")
            is_flagged  = int(is_flag_str.split("(")[1].rstrip(")"))

        with c2:
            old_bal_orig = st.number_input("Sender Opening Bal.", min_value=0.0,
                                           value=1000000.0, key="alt_obo")
            new_bal_orig = st.number_input("Sender Closing Bal.", min_value=0.0,
                                           value=50000.0, key="alt_nbo")
            old_bal_dest = st.number_input("Receiver Opening Bal.", min_value=0.0,
                                           value=0.0, key="alt_obd")
            new_bal_dest = st.number_input("Receiver Closing Bal.", min_value=0.0,
                                           value=950000.0, key="alt_nbd")

        gen_alert = st.button("🚨 Trigger Alert Engine")

        if gen_alert:
            payload = {
                "step": step, "type": txn_type, "amount": amount,
                "oldbalanceOrg": old_bal_orig, "newbalanceOrig": new_bal_orig,
                "oldbalanceDest": old_bal_dest, "newbalanceDest": new_bal_dest,
                "isFlaggedFraud": is_flagged,
            }

            try:
                resp = requests.post(f"{API_BASE}/alert", json=payload, timeout=5)
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.ConnectionError:
                st.error("❌ FastAPI backend unreachable.")
                return
            except Exception as e:
                st.error(f"❌ {e}")
                return

            alert_id = data.get("alert_id", "ALT-???")
            severity = data.get("severity", "Critical")
            status   = data.get("status", "Open")
            sev_col  = SEVERITY_COLOR.get(severity, "#ff4b4b")

            st.markdown(
                f"""
                <div style="background:{sev_col}15;border:1px solid {sev_col}55;
                            border-radius:10px;padding:20px;margin-top:12px;">
                    <div style="font-size:0.75rem;color:#6b7a99;text-transform:uppercase;
                                letter-spacing:0.08em;">New Alert Generated</div>
                    <div style="font-size:1.6rem;font-weight:900;
                                color:{sev_col};margin:8px 0;">{alert_id}</div>
                    <div style="display:flex;gap:24px;font-size:0.9rem;">
                        <span>Severity: <strong style="color:{sev_col};">{severity}</strong></span>
                        <span>Status: <strong style="color:#c9d1e0;">{status}</strong></span>
                        <span>Time: <strong style="color:#c9d1e0;">
                            {datetime.now().strftime('%H:%M:%S')}</strong></span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Charts ───────────────────────────────────────────────────────────────
    col_pie, col_timeline = st.columns([1, 2])
    with col_pie:
        st.plotly_chart(_severity_donut(sample_df), use_container_width=True)
    with col_timeline:
        st.plotly_chart(_timeline_chart(sample_df), use_container_width=True)

    st.markdown("---")

    # ── Alert table ───────────────────────────────────────────────────────────
    st.markdown("#### 📋 Alert Feed")

    # Filters
    f1, f2, f3 = st.columns(3)
    with f1:
        sev_filter = st.multiselect(
            "Severity", ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"],
        )
    with f2:
        status_filter = st.multiselect(
            "Status", ["Open", "In Progress", "Closed"],
            default=["Open"],
        )
    with f3:
        sort_col = st.selectbox("Sort by", ["Risk Score", "Timestamp", "Amount"])

    filtered = sample_df.copy()
    if sev_filter:
        filtered = filtered[filtered["Severity"].isin(sev_filter)]
    if status_filter:
        filtered = filtered[filtered["Status"].isin(status_filter)]
    filtered = filtered.sort_values(sort_col, ascending=False).reset_index(drop=True)

    st.dataframe(
        filtered.style.apply(
            lambda row: [
                f"color: {SEVERITY_COLOR.get(row['Severity'], '#c9d1e0')}"
                if col == "Severity" else ""
                for col in filtered.columns
            ],
            axis=1,
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        f"Showing {len(filtered)} of {len(sample_df)} alerts · "
        f"Last refreshed: {datetime.now().strftime('%H:%M:%S')}"
    )
