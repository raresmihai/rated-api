from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class RawTransaction(BaseModel):
    hash: str
    nonce: int
    block_hash: str
    block_number: int
    transaction_index: int
    from_address: str
    to_address: str
    value: int
    gas: int
    gas_price: int
    block_timestamp: datetime
    max_fee_per_gas: Optional[int]
    max_priority_fee_per_gas: Optional[int]
    transaction_type: int
    receipts_cumulative_gas_used: int
    receipts_gas_used: int
    receipts_contract_address: Optional[str]
    receipts_root: Optional[str]
    receipts_status: int
    receipts_effective_gas_price: int

    @validator('block_timestamp', pre=True)
    def handle_utc_timestamp(cls, v):
        return v.replace(' UTC', '+00:00')

    @validator('max_fee_per_gas', 'max_priority_fee_per_gas', pre=True)
    def handle_empty_values(cls, v):
        return int(v) if v else None
