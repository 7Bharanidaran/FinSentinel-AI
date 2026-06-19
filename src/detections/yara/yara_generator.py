def generate_yara_rule(amount):

    rule = f"""
rule Suspicious_Financial_Transaction
{{
    meta:
        description = "High-value fraud transaction"

    condition:
        amount > {amount}
}}
"""

    return rule

