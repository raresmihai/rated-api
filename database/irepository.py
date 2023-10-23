from abc import ABC, abstractmethod
from typing import Optional
from models.processed_transaction import ProcessedTransaction

class IRepository(ABC):

    @abstractmethod
    def create(self, transaction: ProcessedTransaction) -> None:
        pass

    @abstractmethod
    def get_by_hash(self, hash: str) -> Optional[ProcessedTransaction]:
        pass
