from pydantic import BaseModel

class Transaction(BaseModel):
    step:int
    type:int
    amount:float
    oldbalanceOrg:float
    newbalanceOrig:float
    oldbalanceDest:float
    newbalanceDest:float
    isFlaggedFraud:int

