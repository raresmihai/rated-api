from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from .processed_transaction import ProcessedTransaction

class IRepository(ABC):
    """
    An abstract base class representing a repository interface for processed transactions.
    """
    
    @abstractmethod
    def create(self, transaction: ProcessedTransaction) -> None:
        pass

    @abstractmethod
    def get_by_hash(self, hash: str) -> Optional[ProcessedTransaction]:
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        pass