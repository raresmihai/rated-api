import pickle

from typing import Optional
from database.irepository import IRepository
from models.processed_transaction import ProcessedTransaction

class InMemoryRepository(IRepository):
    def __init__(self):
        self._data_source = {}

    def create(self, transaction: ProcessedTransaction) -> None:
        self._data_source[transaction.hash] = transaction

    def get_by_hash(self, hash: str) -> Optional[ProcessedTransaction]:
        return self._data_source.get(hash)

    def save(self, filepath: str) -> None:
        """Save the data source to a file."""
        with open(filepath, 'wb') as file:
            pickle.dump(self._data_source, file)

    def load(self, filepath: str) -> None:
        """Load the data source from a file."""
        with open(filepath, 'rb') as file:
            self._data_source = pickle.load(file)
