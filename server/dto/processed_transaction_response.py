from pydantic import BaseModel, validator
from datetime import datetime

class ProcessedTransactionResponse(BaseModel):
    hash: str
    fromAddress: str
    toAddress: str
    blockNumber: int
    executedAt: datetime
    gasUsed: int
    gasCostInDollars: float

    @validator('gasCostInDollars', pre=True, always=True)
    def round_gas_cost(cls, value):
        return round(value, 2)