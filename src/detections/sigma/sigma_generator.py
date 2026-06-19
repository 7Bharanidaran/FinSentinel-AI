def generate_sigma_rule(amount):

    rule = f"""
title: High Value Fraud Transaction

id: 001

status: experimental

description: Detects suspicious high-value transactions

logsource:
    product: financial

detection:
    selection:
        amount: > {amount}

condition: selection

level: high
"""

    return rule

