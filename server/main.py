from fastapi import FastAPI, HTTPException
from database.sql_repository import SqlRepository
from server.dto.processed_transaction_response import ProcessedTransactionResponse
from server.dto.stats_response import StatsResponse

app = FastAPI()
repository = SqlRepository()

@app.get("/transactions/{hash}", response_model=ProcessedTransactionResponse)
def get_transaction(hash: str):
    transaction = repository.get_by_hash(hash)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return ProcessedTransactionResponse(
        hash=transaction.hash,
        fromAddress=transaction.fromAddress,
        toAddress=transaction.toAddress,
        blockNumber=transaction.blockNumber,
        executedAt=transaction.executedAt,
        gasUsed=transaction.gasUsed,
        gasCostInDollars=transaction.gasCostInDollars,
    )

@app.get("/stats", response_model=StatsResponse)
def get_stats():
    stats = repository.get_stats()
    return stats

if __name__ == "__main__":
    from database import database
    database.init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
