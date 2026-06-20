
import streamlit as st
import requests
import yaml
import pandas as pd
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

TYPE_MAP = {
    "CASH_IN": 0, "CASH_OUT": 1, "DEBIT": 2, "PAYMENT": 3, "TRANSFER": 4,
}

# ── Sample built-in Sigma rules library ──────────────────────────────────────
SAMPLE_RULES = [
    {
        "id": "SIG-001",
        "title": "High Value Transfer Detected",
        "level": "high",
        "status": "stable",
        "description": "Detects transfers above $500,000 from an account.",
        "logsource": {"category": "financial_transaction"},
        "detection": {
            "selection": {"type": "TRANSFER", "amount|gte": 500000},
            "condition": "selection",
        },
        "falsepositives": ["Legitimate large wire transfers"],
        "tags": ["fraud", "aml", "wire-transfer"],
    },
    {
        "id": "SIG-002",
        "title": "Account Balance Drain",
        "level": "critical",
        "status": "stable",
        "description": "Detects when sender balance drops to near-zero after a transaction.",
        "logsource": {"category": "financial_transaction"},
        "detection": {
            "selection": {"newbalanceOrig|lte": 100, "amount|gte": 10000},
            "condition": "selection",
        },
        "falsepositives": ["Customer closing account voluntarily"],
        "tags": ["fraud", "account-takeover"],
    },
    {
        "id": "SIG-003",
        "title": "Flagged Transaction Bypass",
        "level": "medium",
        "status": "experimental",
        "description": "Transaction was system-flagged but still processed.",
        "logsource": {"category": "financial_transaction"},
        "detection": {
            "selection": {"isFlaggedFraud": 1},
            "condition": "selection",
        },
        "falsepositives": ["Test transactions in UAT environment"],
        "tags": ["fraud", "policy-violation"],
    },
]

LEVEL_COLOR = {
    "critical": "#ff4b4b", "high": "#ff9933",
    "medium": "#c8e63b",   "low": "#00d4ff", "informational": "#8899aa",
}


def _rule_to_yaml(rule: dict) -> str:
    return yaml.dump(rule, default_flow_style=False, sort_keys=False)


def render():
    st.markdown("# 🛡️ Sigma Rule Generation")
    st.markdown(
        "Generate **SIEM-ready Sigma detection rules** from transaction data. "
        "Rules can be exported to Splunk, Elastic, QRadar, Microsoft Sentinel, and more."
    )
    st.markdown("---")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_gen, tab_lib = st.tabs(["⚡ Generate Rule", "📚 Rule Library"])

    # ── Tab 1: Generate ───────────────────────────────────────────────────────
    with tab_gen:
        st.markdown("#### 📋 Transaction Input")
        c1, c2 = st.columns(2)

        with c1:
            step = st.number_input("Step", min_value=1, value=1, key="sig_step")
            txn_type_label = st.selectbox("Type", list(TYPE_MAP.keys()),
                                          index=4, key="sig_type")
            txn_type = TYPE_MAP[txn_type_label]
            amount = st.number_input("Amount (USD)", min_value=0.0,
                                     value=950000.0, step=10000.0, key="sig_amt")
            is_flagged_val = st.selectbox("System-Flagged?",
                                          ["No (0)", "Yes (1)"], key="sig_flag")
            is_flagged = int(is_flagged_val.split("(")[1].rstrip(")"))

        with c2:
            old_bal_orig = st.number_input("Sender Opening Bal.", min_value=0.0,
                                           value=1000000.0, key="sig_obo")
            new_bal_orig = st.number_input("Sender Closing Bal.", min_value=0.0,
                                           value=50000.0, key="sig_nbo")
            old_bal_dest = st.number_input("Receiver Opening Bal.", min_value=0.0,
                                           value=0.0, key="sig_obd")
            new_bal_dest = st.number_input("Receiver Closing Bal.", min_value=0.0,
                                           value=950000.0, key="sig_nbd")

        gen_btn = st.button("🛡️ Generate Sigma Rule")

        if gen_btn:
            payload = {
                "step": step, "type": txn_type, "amount": amount,
                "oldbalanceOrg": old_bal_orig, "newbalanceOrig": new_bal_orig,
                "oldbalanceDest": old_bal_dest, "newbalanceDest": new_bal_dest,
                "isFlaggedFraud": is_flagged,
            }

            try:
                resp = requests.post(f"{API_BASE}/sigma-rule", json=payload, timeout=5)
                resp.raise_for_status()
                data = resp.json()
            except requests.exceptions.ConnectionError:
                st.error("❌ FastAPI backend unreachable.")
                return
            except Exception as e:
                st.error(f"❌ {e}")
                return

            title = data.get("title", "Unknown Rule")
            level = data.get("level", "medium")
            level_color = LEVEL_COLOR.get(level, "#8899aa")

            st.markdown("---")
            st.markdown("#### ✅ Generated Sigma Rule")

            # Rule metadata cards
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rule ID", f"SIG-{datetime.now().strftime('%H%M%S')}")
            m2.metric("Level", level.capitalize())
            m3.metric("Status", "Experimental")
            m4.metric("Type", txn_type_label)

            # Build full Sigma rule dict
            full_rule = {
                "title": title,
                "id": f"finsentinel-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "experimental",
                "description": (
                    f"Auto-generated rule for {txn_type_label} "
                    f"transaction of ${amount:,.2f}"
                ),
                "date": datetime.now().strftime("%Y/%m/%d"),
                "author": "FinSentinel-AI",
                "level": level,
                "logsource": {"category": "financial_transaction", "product": "finsentinel"},
                "detection": {
                    "selection": {
                        "type": txn_type_label,
                        "amount|gte": amount * 0.9,
                        "newbalanceOrig|lte": new_bal_orig * 1.1,
                    },
                    "condition": "selection",
                },
                "falsepositives": ["Legitimate large transfers — verify with customer"],
                "tags": ["fraud", "aml", level],
            }

            # Display as YAML
            rule_yaml = _rule_to_yaml(full_rule)
            st.code(rule_yaml, language="yaml")

            # Export hint
            st.markdown(
                f"""
                <div class="alert-high">
                    🛡️ Copy the rule above and import into your SIEM.
                    Supported platforms: <strong>Splunk · Elastic · QRadar ·
                    Microsoft Sentinel · Chronicle</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Tab 2: Library ────────────────────────────────────────────────────────
    with tab_lib:
        st.markdown("#### 📚 Built-in Rule Library")
        st.caption(f"{len(SAMPLE_RULES)} rules · Updated daily")

        # Summary table
        summary_df = pd.DataFrame([
            {
                "ID": r["id"],
                "Title": r["title"],
                "Level": r["level"].capitalize(),
                "Status": r["status"].capitalize(),
                "Tags": ", ".join(r["tags"]),
            }
            for r in SAMPLE_RULES
        ])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### 🔍 Inspect Rule")
        selected_id = st.selectbox(
            "Select rule to view", [r["id"] for r in SAMPLE_RULES]
        )
        selected = next(r for r in SAMPLE_RULES if r["id"] == selected_id)
        level_col = LEVEL_COLOR.get(selected["level"], "#8899aa")

        # Level badge
        st.markdown(
            f"""<span class="badge" style="background:{level_col}22;
                color:{level_col};border:1px solid {level_col}55;
                font-size:0.8rem;padding:4px 12px;border-radius:999px;">
                {selected['level'].upper()}
            </span>""",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{selected['title']}**")
        st.caption(selected["description"])
        st.code(_rule_to_yaml(selected), language="yaml")
