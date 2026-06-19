from fastapi import FastAPI
from schemas import Transaction

app = FastAPI()


@app.get("/")
def home():
    return {
        "message":"Welcome to FinSentinel-AI"
    }


@app.post("/predict")
def predict(transaction: Transaction):

    return {
        "fraud_probability":0.96
    }


@app.post("/risk-score")
def risk_score(transaction: Transaction):

    return {
        "risk_score":96,
        "risk_level":"Critical"
    }


@app.post("/recommendation")
def recommendation(transaction: Transaction):

    return {
        "recommendation":"Block Transaction"
    }


@app.post("/sigma-rule")
def sigma_rule(transaction: Transaction):

    return {
        "title":"High Value Fraud Transaction",
        "level":"high"
    }


@app.post("/yara-rule")
def yara_rule(transaction: Transaction):

    return {
        "rule":"Suspicious_Financial_Transaction",
        "threshold":900000
    }


@app.post("/alert")
def alert(transaction: Transaction):

    return {
        "alert_id":"ALT-1001",
        "severity":"Critical",
        "status":"Open"
    }
