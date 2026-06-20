"""
yara_rules.py — FinSentinel-AI YARA Rule Generation Page
Calls /yara-rule API and renders endpoint-ready YARA detection rules.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

TYPE_MAP = {
    "CASH_IN": 0, "CASH_OUT": 1, "DEBIT": 2, "PAYMENT": 3, "TRANSFER": 4,
}

# ── Built-in YARA rule templates ─────────────────────────────────────────────
SAMPLE_YARA = [
    {
        "id": "YAR-001",
        "name": "Suspicious_High_Value_Transaction",
        "level": "Critical",
        "description": "Detects financial transactions exceeding $900,000.",
        "rule": """\
rule Suspicious_High_Value_Transaction
{
    meta:
        author      = "FinSentinel-AI"
        description = "Detects transactions above $900,000"
        severity    = "critical"
        date        = "2024-01-01"

    strings:
        $txn_type = "TRANSFER"
        $txn_type2 = "CASH_OUT"

    condition:
        (any of ($txn_type*)) and
        amount > 900000
}""",
    },
    {
        "id": "YAR-002",
        "name": "Account_Drain_Pattern",
        "level": "High",
        "description": "Detects complete balance drain — account emptied in one transaction.",
        "rule": """\
rule Account_Drain_Pattern
{
    meta:
        author      = "FinSentinel-AI"
        description = "Sender balance drops to zero after transaction"
        severity    = "high"
        date        = "2024-01-01"

    condition:
        newbalanceOrig <= 0 and
        oldbalanceOrg  > 50000
}""",
    },
    {
        "id": "YAR-003",
        "name": "Zero_Receiver_Balance_Injection",
        "level": "Medium",
        "description": "Receiver had zero balance before receiving large sum — money mule indicator.",
        "rule": """\
rule Zero_Receiver_Balance_Injection
{
    meta:
        author      = "FinSentinel-AI"
        description = "Funds sent to previously empty receiver account"
        severity    = "medium"
        date        = "2024-01-01"

    condition:
        oldbalanceDest == 0 and
        newbalanceDest  > 100000
}""",
    },
]

LEVEL_COLOR = {
    "Critical": "#ff4b4b", "High": "#ff9933",
    "Medium": "#c8e63b",   "Low": "#00d4ff",
}


def _build_yara_rule(
    rule_name: str,
    txn_type: str,
    amount: float,
    threshold_pct: float,
    new_bal_orig: float,
    old_bal_dest: float,
    new_bal_dest: float,
) -> str:
    threshold = amount * (1 - threshold_pct / 100)
    drain = new_bal_orig < 1000
    mule  = old_bal_dest == 0 and new_bal_dest > 100000

    conds = [f"amount > {threshold:.0f}"]
    if drain:
        conds.append("newbalanceOrig <= 1000")
    if mule:
        conds.append("oldbalanceDest == 0")
        conds.append(f"newbalanceDest > {new_bal_dest * 0.8:.0f}")

    condition_block = " and\n        ".join(conds)

    return f"""\
rule {rule_name}
{{
    meta:
        author      = "FinSentinel-AI"
        description = "Auto-generated rule — {txn_type} transaction"
        severity    = "high"
        generated   = "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    strings:
        $txn_type = "{txn_type}"

    condition:
        $txn_type and
        {condition_block}
}}"""


def render():
    st.markdown("# 🧬 YARA Rule Generation")
    st.markdown(
        "Generate **endpoint-ready YARA detection rules** for financial threat hunting. "
        "Rules can be deployed on any YARA-compatible engine or EDR platform."
    )
    st.markdown("---")

    tab_gen, tab_lib = st.tabs(["⚡ Generate Rule", "📚 Rule Library"])

    # ── Tab 1: Generate ───────────────────────────────────────────────────────
    with tab_gen:
        st.markdown("#### 📋 Transaction Input")
        c1, c2 = st.columns(2)

        with c1:
            step        = st.number_input("Step", min_value=1, value=1, key="yar_step")
            txn_lbl     = st.selectbox("Transaction Type", list(TYPE_MAP.keys()),
                                       index=4, key="yar_type")
            txn_type    = TYPE_MAP[txn_lbl]
            amount      = st.number_input("Amount (USD)", min_value=0.0,
                                          value=950000.0, step=10000.0, key="yar_amt")
            is_flag_str = st.selectbox("System-Flagged?",
                                       ["No (0)", "Yes (1)"], key="yar_flag")
            is_flagged  = int(is_flag_str.split("(")[1].rstrip(")"))

        with c2:
            old_bal_orig = st.number_input("Sender Opening Bal.", min_value=0.0,
                                           value=1000000.0, key="yar_obo")
            new_bal_orig = st.number_input("Sender Closing Bal.", min_value=0.0,
                                           value=50000.0, key="yar_nbo")
            old_bal_dest = st.number_input("Receiver Opening Bal.", min_value=0.0,
                                           value=0.0, key="yar_obd")
            new_bal_dest = st.number_input("Receiver Closing Bal.", min_value=0.0,
                                           value=950000.0, key="yar_nbd")

        threshold_pct = st.slider(
            "Amount Threshold Sensitivity (%)",
            min_value=0, max_value=50, value=10,
            help="Lower = more strict; 0% = flag exact amount, 50% = flag ≥50% of amount",
        )
        rule_name = st.text_input(
            "Rule Name",
            value=f"FinSentinel_{txn_lbl}_{datetime.now().strftime('%H%M%S')}",
        )

        gen_btn = st.button("🧬 Generate YARA Rule")

        if gen_btn:
            payload = {
                "step": step, "type": txn_type, "amount": amount,
                "oldbalanceOrg": old_bal_orig, "newbalanceOrig": new_bal_orig,
                "oldbalanceDest": old_bal_dest, "newbalanceDest": new_bal_dest,
                "isFlaggedFraud": is_flagged,
            }

            # API call (for metadata)
            try:
                resp = requests.post(f"{API_BASE}/yara-rule", json=payload, timeout=5)
                resp.raise_for_status()
                api_data = resp.json()
            except requests.exceptions.ConnectionError:
                st.error("❌ FastAPI backend unreachable.")
                return
            except Exception as e:
                st.error(f"❌ {e}")
                return

            # Build full rule locally
            yara_text = _build_yara_rule(
                rule_name, txn_lbl, amount, threshold_pct,
                new_bal_orig, old_bal_dest, new_bal_dest,
            )

            st.markdown("---")
            st.markdown("#### ✅ Generated YARA Rule")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rule", api_data.get("rule", rule_name))
            m2.metric("Threshold", f"${api_data.get('threshold', amount):,}")
            m3.metric("Transaction Type", txn_lbl)
            m4.metric("Amount", f"${amount:,.0f}")

            st.code(yara_text, language="text")

            # Deployment targets
            st.markdown(
                """
                <div class="alert-medium">
                    🧬 Deploy this rule to: <strong>YARA · VirusTotal · CrowdStrike Falcon ·
                    Microsoft Defender · Carbon Black · Elastic Endpoint Security</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("📦 Raw API Response"):
                st.json(api_data)

    # ── Tab 2: Library ────────────────────────────────────────────────────────
    with tab_lib:
        st.markdown("#### 📚 Built-in YARA Rule Library")
        st.caption(f"{len(SAMPLE_YARA)} rules · FinSentinel-AI Threat Intelligence")

        summary_df = pd.DataFrame([
            {"ID": r["id"], "Name": r["name"],
             "Level": r["level"], "Description": r["description"]}
            for r in SAMPLE_YARA
        ])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        selected_id = st.selectbox(
            "Inspect Rule", [r["id"] for r in SAMPLE_YARA], key="yar_lib_sel"
        )
        selected = next(r for r in SAMPLE_YARA if r["id"] == selected_id)
        lc = LEVEL_COLOR.get(selected["level"], "#8899aa")

        st.markdown(
            f"""<span style="background:{lc}22;color:{lc};border:1px solid {lc}55;
                padding:4px 12px;border-radius:999px;font-size:0.8rem;font-weight:700;">
                {selected['level'].upper()}
            </span> &nbsp; <strong>{selected['name']}</strong>""",
            unsafe_allow_html=True,
        )
        st.caption(selected["description"])
        st.code(selected["rule"], language="text")
