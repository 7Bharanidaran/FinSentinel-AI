"""
explainability.py — FinSentinel-AI SHAP Explainability Page
Visualizes feature importance and SHAP values for model transparency.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


# ── Sample SHAP values (replace with real shap.Explainer output) ─────────────
FEATURES = [
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "type",
    "step",
    "isFlaggedFraud",
]

# Simulated mean |SHAP| values for global importance
GLOBAL_SHAP = [0.38, 0.24, 0.21, 0.18, 0.14, 0.09, 0.05, 0.04]


def _global_importance_chart() -> go.Figure:
    df = pd.DataFrame({"Feature": FEATURES, "Mean |SHAP|": GLOBAL_SHAP})
    df = df.sort_values("Mean |SHAP|")

    fig = go.Figure(
        go.Bar(
            x=df["Mean |SHAP|"],
            y=df["Feature"],
            orientation="h",
            marker=dict(
                color=df["Mean |SHAP|"],
                colorscale=[[0, "#0a4a6e"], [0.5, "#0057ff"], [1, "#ff4b4b"]],
                showscale=True,
                colorbar=dict(title="Impact", tickfont={"color": "#c9d1e0"}),
            ),
        )
    )
    fig.update_layout(
        title="Global Feature Importance (Mean |SHAP|)",
        paper_bgcolor="#111827",
        plot_bgcolor="#0a0e1a",
        font={"color": "#c9d1e0"},
        xaxis=dict(title="Mean |SHAP| Value", gridcolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
    )
    return fig


def _waterfall_chart(shap_values: list[float]) -> go.Figure:
    """SHAP waterfall for a single prediction."""
    base_value = 0.12  # E[f(x)] — model base prediction

    fig = go.Figure(
        go.Waterfall(
            orientation="h",
            measure=["relative"] * len(FEATURES) + ["total"],
            x=shap_values + [sum(shap_values)],
            y=FEATURES + ["Prediction"],
            base=base_value,
            decreasing={"marker": {"color": "#00d4ff"}},
            increasing={"marker": {"color": "#ff4b4b"}},
            totals={"marker": {"color": "#c8e63b"}},
            connector={"line": {"color": "#1e2d45"}},
        )
    )
    fig.update_layout(
        title="SHAP Waterfall — Single Transaction",
        paper_bgcolor="#111827",
        plot_bgcolor="#0a0e1a",
        font={"color": "#c9d1e0"},
        xaxis=dict(title="SHAP Value", gridcolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=380,
    )
    return fig


def _beeswarm_placeholder() -> go.Figure:
    """Simulated SHAP beeswarm / summary dot plot."""
    np.random.seed(42)
    rows = []
    for feat, base_shap in zip(FEATURES, GLOBAL_SHAP):
        for _ in range(60):
            feat_val = np.random.random()
            shap_val = np.random.normal(
                base_shap * (1 if feat_val > 0.5 else -1),
                base_shap * 0.4,
            )
            rows.append({"Feature": feat, "SHAP Value": shap_val, "Feature Value": feat_val})

    df = pd.DataFrame(rows)
    fig = px.strip(
        df, x="SHAP Value", y="Feature", color="Feature Value",
        color_continuous_scale=[[0, "#0057ff"], [0.5, "#c8e63b"], [1, "#ff4b4b"]],
        title="SHAP Summary Plot (Simulated Distribution)",
    )
    fig.update_traces(jitter=0.4, marker_size=4, opacity=0.7)
    fig.update_layout(
        paper_bgcolor="#111827",
        plot_bgcolor="#0a0e1a",
        font={"color": "#c9d1e0"},
        xaxis=dict(gridcolor="#1e2d45", zeroline=True, zerolinecolor="#3a4a60"),
        yaxis=dict(gridcolor="#1e2d45"),
        coloraxis_colorbar=dict(title="Feature Value", tickfont={"color": "#c9d1e0"}),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    return fig


def render():
    st.markdown("# 📈 SHAP Explainability")
    st.markdown(
        "Understand *why* the model made each decision. "
        "SHAP (SHapley Additive exPlanations) attributes every prediction "
        "to individual input features."
    )
    st.markdown("---")

    # ── Concept cards ────────────────────────────────────────────────────────
    st.markdown("#### 🧠 SHAP Concepts")
    concepts = [
        ("🔵 Negative SHAP", "Feature pushed prediction toward legitimate (lower fraud risk)."),
        ("🔴 Positive SHAP", "Feature pushed prediction toward fraud (higher fraud risk)."),
        ("⚖️ Base Value",    "E[f(x)] — average model output over the training dataset."),
        ("📏 |SHAP|",        "Absolute magnitude = overall importance, regardless of direction."),
    ]
    cols = st.columns(4)
    for col, (title, desc) in zip(cols, concepts):
        with col:
            st.markdown(
                f"""
                <div style="background:#111827;border:1px solid #1e2d45;
                            border-radius:8px;padding:16px;height:110px;">
                    <div style="color:#e2e8f0;font-weight:700;font-size:0.9rem;">{title}</div>
                    <div style="color:#6b7a99;font-size:0.8rem;margin-top:6px;
                                line-height:1.5;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # ── Global importance ────────────────────────────────────────────────────
    st.markdown("#### 📊 Global Feature Importance")
    st.plotly_chart(_global_importance_chart(), use_container_width=True)

    # ── Single-transaction waterfall ─────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🌊 Waterfall Explanation — Live Transaction")
    st.markdown(
        "Adjust the sliders to simulate how each feature shifts the fraud probability."
    )

    col_sliders, col_chart = st.columns([1, 2])

    with col_sliders:
        shap_vals = []
        defaults = [0.32, -0.12, -0.09, 0.08, 0.07, -0.05, 0.02, 0.01]
        for feat, default in zip(FEATURES, defaults):
            val = st.slider(
                f"{feat}", -0.5, 0.5, float(default), 0.01,
                label_visibility="visible",
            )
            shap_vals.append(val)

    with col_chart:
        st.plotly_chart(_waterfall_chart(shap_vals), use_container_width=True)

    # ── Beeswarm ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🐝 SHAP Summary Plot (Distribution over Dataset)")
    st.caption(
        "Each dot is one transaction. Color = feature value (blue = low, red = high). "
        "X-axis = SHAP impact on model output. "
        "*(Simulated distribution — replace with real shap.summary_plot data.)*"
    )
    st.plotly_chart(_beeswarm_placeholder(), use_container_width=True)

    # ── Feature table ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Feature Importance Table")
    df_table = pd.DataFrame({
        "Rank": range(1, len(FEATURES) + 1),
        "Feature": FEATURES,
        "Mean |SHAP|": GLOBAL_SHAP,
        "Direction": ["↑ Fraud" if v > 0.1 else "↓ Legit" for v in GLOBAL_SHAP],
    }).sort_values("Mean |SHAP|", ascending=False).reset_index(drop=True)
    st.dataframe(df_table, use_container_width=True, hide_index=True)
