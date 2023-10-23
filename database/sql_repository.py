from typing import Optional
from .irepository import IRepository
from database.database import get_db_session
from models.processed_transaction import ProcessedTransaction

class SqlRepository(IRepository):

    def create(self, transaction: ProcessedTransaction) -> None:
        with get_db_session() as session:
            session.add(transaction)
            session.commit()

    def get_by_hash(self, hash: str) -> Optional[ProcessedTransaction]:
        with get_db_session() as session:
            transaction = session.query(ProcessedTransaction).filter_by(hash=hash).first()
            return transaction
