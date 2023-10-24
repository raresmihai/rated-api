from fastapi import APIRouter, HTTPException
from server.response_models import ProcessedTransactionResponse, StatsResponse

def get_api_router(repository):
    """
    Create an API router for handling transaction-related endpoints.

    Args:
        repository: An instance of a repository for database operations.

    Returns:
        APIRouter: An API router for transaction-related endpoints.

    """

    router = APIRouter()

    @router.get("/transactions/{hash}", response_model=ProcessedTransactionResponse)
    def get_transaction(hash: str):
        """
        Get transaction details by hash.

        Args:
            hash (str): The hash of the transaction to retrieve.

        Returns:
            ProcessedTransactionResponse: The response containing transaction details.

        Raises:
            HTTPException: If the transaction is not found, returns a 404 status code.

        """        
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

    @router.get("/stats", response_model=StatsResponse)
    def get_stats():
        """
        Get statistics for transactions.

        Returns:
            StatsResponse: The response containing transaction statistics.

        """        
        stats = repository.get_stats()
        return stats
    
    return router
