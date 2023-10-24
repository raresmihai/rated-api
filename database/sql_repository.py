from typing import Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from .irepository import IRepository
from .database import get_db_session
from .processed_transaction import ProcessedTransaction

class SqlRepository(IRepository):
    """
    A repository class for handling database operations related to ProcessedTransaction objects.

    This class provides methods for creating and retrieving ProcessedTransaction objects in a SQL database.
    """
    
    def create(self, transaction: ProcessedTransaction) -> None:
        with get_db_session() as session:
            try:
                session.add(transaction)
                session.commit()
            except IntegrityError:
                # Handle the error (e.g., log it, update the record, etc.)
                print(f"[SqlRepository] Duplicate transaction detected with hash {transaction.hash}")
                session.rollback()

    def get_by_hash(self, hash: str) -> Optional[ProcessedTransaction]:
        with get_db_session() as session:
            transaction = session.query(ProcessedTransaction).filter_by(hash=hash).first()
            if transaction:
                # detach the object from the session
                session.expunge(transaction)
            return transaction

    def get_stats(self) -> Dict[str, Any]:
        with get_db_session() as session:
            sql = text("""
            SELECT
                COUNT(*) as totalTransactionsInDB,
                SUM(gasUsed) as totalGasUsed,
                SUM(gasCostInDollars) as totalGasCostInDollars
            FROM
                processed_transaction
            """)
            result = session.execute(sql).fetchone()

            total_transactions_in_db = result[0] if result else 0
            total_gas_used = result[1] if result else 0
            total_gas_cost_in_dollars = result[2] if result else 0.0

            return {
                "totalTransactionsInDB": total_transactions_in_db,
                "totalGasUsed": total_gas_used,
                "totalGasCostInDollars": round(total_gas_cost_in_dollars, 2)
            }
