"""
analytics.py — FinSentinel-AI Analytics Dashboard Page
Full visual analytics: risk distribution, fraud trends, severity breakdown,
transaction volume, and model performance metrics.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Reproducible sample data ─────────────────────────────────────────────────
np.random.seed(42)
N = 500


def _make_sample_data() -> pd.DataFrame:
    types      = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
    severities = ["Critical", "High", "Medium", "Low"]

    df = pd.DataFrame({
        "transaction_id": [f"TXN-{10000 + i}" for i in range(N)],
        "amount":         np.random.exponential(scale=150_000, size=N).clip(1_000, 2_000_000),
        "type":           np.random.choice(types, size=N, p=[0.1, 0.25, 0.1, 0.3, 0.25]),
        "fraud":          np.random.choice([0, 1], size=N, p=[0.92, 0.08]),
        "risk_score":     np.random.beta(a=2, b=5, size=N) * 100,
        "severity":       np.random.choice(severities, size=N, p=[0.08, 0.22, 0.35, 0.35]),
        "hour":           np.random.randint(0, 24, size=N),
        "day":            np.random.choice(
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            size=N, p=[0.17, 0.17, 0.17, 0.17, 0.17, 0.08, 0.07],
        ),
        "precision":      0.962,
        "recall":         0.941,
        "f1":             0.951,
        "auc":            0.987,
    })
    return df


SEVERITY_COLOR = {
    "Critical": "#ff4b4b", "High": "#ff9933",
    "Medium": "#c8e63b",   "Low": "#00d4ff",
}


def render():
    st.markdown("# 📊 Analytics Dashboard")
    st.markdown(
        "Platform-wide analytics: transaction volumes, fraud trends, "
        "risk distributions, and ML model performance."
    )
    st.markdown("---")

    df = _make_sample_data()
    fraud_df  = df[df["fraud"] == 1]
    legit_df  = df[df["fraud"] == 0]

    # ── KPI strip ────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Transactions", f"{N:,}")
    k2.metric("Fraud Count", len(fraud_df), f"{len(fraud_df)/N*100:.1f}%")
    k3.metric("Total Volume", f"${df['amount'].sum()/1e6:.1f}M")
    k4.metric("Model AUC-ROC", "0.987")
    k5.metric("Avg Risk Score", f"{df['risk_score'].mean():.1f}")

    st.markdown("---")

    # ── Row 1: Risk distribution + Fraud donut ────────────────────────────────
    st.markdown("#### 📈 Risk & Fraud Distribution")
    r1c1, r1c2 = st.columns(2)

    with r1c1:
        # Risk score histogram
        fig_risk = px.histogram(
            df, x="risk_score", nbins=40, color="severity",
            color_discrete_map=SEVERITY_COLOR,
            title="Risk Score Distribution",
            labels={"risk_score": "Risk Score (0–100)", "count": "Transactions"},
        )
        fig_risk.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#0a0e1a",
            font={"color": "#c9d1e0"},
            xaxis=dict(gridcolor="#1e2d45"),
            yaxis=dict(gridcolor="#1e2d45"),
            legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
            margin=dict(l=10, r=10, t=50, b=10),
            bargap=0.05,
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    with r1c2:
        # Fraud pie
        fraud_counts = df["fraud"].map({0: "Legitimate", 1: "Fraudulent"}).value_counts()
        fig_fraud = px.pie(
            names=fraud_counts.index,
            values=fraud_counts.values,
            hole=0.55,
            color=fraud_counts.index,
            color_discrete_map={"Fraudulent": "#ff4b4b", "Legitimate": "#00d4ff"},
            title="Fraud vs Legitimate Transactions",
        )
        fig_fraud.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font={"color": "#c9d1e0"},
            legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_fraud, use_container_width=True)

    # ── Row 2: Severity donut + Transaction type bar ──────────────────────────
    st.markdown("---")
    st.markdown("#### 🔴 Severity & Transaction Type Breakdown")
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        sev_counts = df["severity"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        fig_sev = px.pie(
            sev_counts, names="Severity", values="Count", hole=0.55,
            color="Severity", color_discrete_map=SEVERITY_COLOR,
            title="Alert Severity Distribution",
        )
        fig_sev.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#111827",
            font={"color": "#c9d1e0"},
            legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_sev, use_container_width=True)

    with r2c2:
        type_fraud = (
            df.groupby(["type", "fraud"])
            .size()
            .reset_index(name="count")
        )
        type_fraud["label"] = type_fraud["fraud"].map({0: "Legitimate", 1: "Fraudulent"})
        fig_type = px.bar(
            type_fraud, x="type", y="count", color="label",
            color_discrete_map={"Fraudulent": "#ff4b4b", "Legitimate": "#00d4ff"},
            title="Fraud by Transaction Type",
            barmode="stack",
        )
        fig_type.update_layout(
            paper_bgcolor="#111827", plot_bgcolor="#0a0e1a",
            font={"color": "#c9d1e0"},
            xaxis=dict(gridcolor="#1e2d45"),
            yaxis=dict(gridcolor="#1e2d45"),
            legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
            margin=dict(l=10, r=10, t=50, b=10),
        )
        st.plotly_chart(fig_type, use_container_width=True)

    # ── Row 3: Heatmap (hour × day) ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🕐 Transaction Volume Heatmap (Hour × Day)")

    day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    heat_df   = (
        df.groupby(["day", "hour"])
        .size()
        .reset_index(name="count")
    )
    heat_pivot = heat_df.pivot(index="day", columns="hour", values="count").fillna(0)
    heat_pivot = heat_pivot.reindex(day_order)

    fig_heat = go.Figure(
        go.Heatmap(
            z=heat_pivot.values,
            x=list(range(24)),
            y=day_order,
            colorscale=[[0, "#0a0e1a"], [0.5, "#0057ff"], [1, "#ff4b4b"]],
            showscale=True,
            colorbar=dict(title="Volume", tickfont={"color": "#c9d1e0"}),
        )
    )
    fig_heat.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#111827",
        font={"color": "#c9d1e0"},
        xaxis=dict(title="Hour of Day", tickcolor="#6b7a99"),
        yaxis=dict(title="Day of Week", tickcolor="#6b7a99"),
        margin=dict(l=10, r=10, t=20, b=10),
        height=300,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ── Row 4: Model performance ──────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🤖 Model Performance Metrics")
    mp1, mp2, mp3, mp4 = st.columns(4)

    metrics = [
        ("Precision", 0.962, "#00d4ff"),
        ("Recall",    0.941, "#c8e63b"),
        ("F1 Score",  0.951, "#ff9933"),
        ("AUC-ROC",   0.987, "#ff4b4b"),
    ]
    for col, (name, val, color) in zip([mp1, mp2, mp3, mp4], metrics):
        with col:
            fig_bullet = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=val * 100,
                    title={"text": name, "font": {"color": "#c9d1e0", "size": 14}},
                    gauge={
                        "axis": {"range": [0, 100], "tickcolor": "#6b7a99"},
                        "bar": {"color": color},
                        "bgcolor": "#111827",
                        "bordercolor": "#1e2d45",
                    },
                    number={"suffix": "%", "font": {"color": color, "size": 28}},
                )
            )
            fig_bullet.update_layout(
                paper_bgcolor="#111827", plot_bgcolor="#111827",
                font={"color": "#c9d1e0"},
                margin=dict(l=10, r=10, t=40, b=10),
                height=200,
            )
            st.plotly_chart(fig_bullet, use_container_width=True)

    # ── Amount scatter ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 💰 Amount vs Risk Score")
    fig_scatter = px.scatter(
        df.sample(200), x="amount", y="risk_score",
        color="severity", size_max=10,
        color_discrete_map=SEVERITY_COLOR,
        opacity=0.7,
        title="Transaction Amount vs Risk Score (Sample of 200)",
        labels={"amount": "Amount (USD)", "risk_score": "Risk Score"},
        hover_data=["type", "fraud"],
    )
    fig_scatter.update_layout(
        paper_bgcolor="#111827", plot_bgcolor="#0a0e1a",
        font={"color": "#c9d1e0"},
        xaxis=dict(gridcolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45"),
        legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Raw data preview ──────────────────────────────────────────────────────
    st.markdown("---")
    with st.expander("📋 Raw Sample Data (first 20 rows)"):
        st.dataframe(
            df[["transaction_id", "type", "amount", "risk_score",
                "severity", "fraud", "hour", "day"]].head(20),
            use_container_width=True,
            hide_index=True,
        )
