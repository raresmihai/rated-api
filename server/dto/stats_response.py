from pydantic import BaseModel, validator

class StatsResponse(BaseModel):
    totalTransactionsInDB: int
    totalGasUsed: int
    totalGasCostInDollars: float
    
    @validator('totalGasCostInDollars', pre=True, always=True)
    def round_totalGasCostInDollars(cls, value):
        return round(value, 2)
