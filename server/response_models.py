from datetime import datetime
from pydantic import BaseModel, validator

"""
Pydantic models representing a responses returned by the API.
"""
class ProcessedTransactionResponse(BaseModel):
    hash: str
    fromAddress: str
    toAddress: str
    blockNumber: int
    executedAt: datetime
    gasUsed: int
    gasCostInDollars: float

    @validator('gasCostInDollars', pre=True)
    def round_gas_cost(cls, value):
        return round(value, 2)

class StatsResponse(BaseModel):
    totalTransactionsInDB: int
    totalGasUsed: int
    totalGasCostInDollars: float

    @validator('totalGasCostInDollars', pre=True)
    def round_totalGasCostInDollars(cls, value):
        return round(value, 2)
