import pickle

from typing import Optional
from database.irepository import IRepository
from .processed_transaction import ProcessedTransaction

"""
NOT USED.

InMemoryRepository that I initially used when building the solution for testing purposes.
Could be used for testing purposes.
"""
class InMemoryRepository(IRepository):
    def __init__(self):
        self._data_source = {}

    def create(self, transaction: ProcessedTransaction) -> None:
        self._data_source[transaction.hash] = transaction

    def get_by_hash(self, hash: str) -> Optional[ProcessedTransaction]:
        return self._data_source.get(hash)

    def get_stats(self):
        totalTransactionsInDB = len(self._data_source)
        totalGasUsed = sum(transaction.gasUsed for transaction in self._data_source.values())
        totalGasCostInDollars = sum(transaction.gasCostInDollars for transaction in self._data_source.values())
        
        return {
            "totalTransactionsInDB": totalTransactionsInDB,
            "totalGasUsed": totalGasUsed,
            "totalGasCostInDollars": totalGasCostInDollars
        }

    def save(self, filepath: str) -> None:
        with open(filepath, 'wb') as file:
            pickle.dump(self._data_source, file)

    def load(self, filepath: str) -> None:
        with open(filepath, 'rb') as file:
            self._data_source = pickle.load(file)
