from pydantic import ValidationError
from datetime import datetime
import csv

from .raw_transaction import RawTransaction
from database import ProcessedTransaction, IRepository
from crypto_data.crypto_to_usd import CryptoToUsd

class CsvProcessor:
    """
    A CSV processor class for handling cryptocurrency transaction data.

    Args:
        crypto_to_usd_instance (CryptoToUsd): An instance of CryptoToUsd for currency conversion.
        db_repository (IRepository): A database repository for storing processed transactions.

    Methods:
        process(file_path: str):
            Process a CSV file containing cryptocurrency transaction data.
        csv_stream(filename: str):
            Generate rows from a CSV file.
        process_raw_transaction(transaction: RawTransaction) -> ProcessedTransaction:
            Process a raw cryptocurrency transaction into a processed transaction.
        compute_gas_cost_in_usd(transaction: RawTransaction) -> float:
            Compute the gas cost of a transaction in USD.

    """
    
    def __init__(self, crypto_to_usd_instance: CryptoToUsd, db_repository: IRepository):
        self.crypto_to_usd_instance = crypto_to_usd_instance
        self.db_repository = db_repository

    def process(self, file_path: str):
        print(f"[CsvProcessor] Processing {file_path}")
        for transaction_event in self.csv_stream(file_path):
            try:
                raw_transaction = RawTransaction(**transaction_event)                
                processed_transaction = self.process_raw_transaction(raw_transaction)
                self.db_repository.create(processed_transaction)
                
            except ValidationError as e:
                # Handle the validation error, log it, emit a metric and alert etc.
                print(f"Error processing transaction: {e}")

            except Exception as ex:
                # TO DO: Emit a metric to alert on failed transactions
                print(f"[CsvProcessor] An unexpected error occurred when processing {transaction_event}. Skipping it.\n{ex}")
                raise ex

    def csv_stream(self, filename: str):
        # TO DO: We'd normally use Kafka or other message broker,
        # but we'll simulate an event stream using generators            
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                yield row

    def process_raw_transaction(self, transaction: RawTransaction):
        gas_cost_usd = self.compute_gas_cost_in_usd(transaction)

        return ProcessedTransaction(
            hash=transaction.hash,
            fromAddress=transaction.from_address,
            toAddress=transaction.to_address,
            blockNumber=transaction.block_number,
            executedAt=transaction.block_timestamp,
            gasUsed=transaction.receipts_gas_used,
            gasCostInDollars=gas_cost_usd
        )

    def compute_gas_cost_in_usd(self, transaction: RawTransaction) -> float:
        gas_cost_wei = transaction.receipts_gas_used * transaction.receipts_effective_gas_price
        gas_cost_gwei = gas_cost_wei / 1e9
        gas_cost_eth = gas_cost_gwei / 1e9
        eth_to_usd = self.crypto_to_usd_instance.get('ethereum', transaction.block_timestamp)
        gas_cost_usd = gas_cost_eth * eth_to_usd

        return gas_cost_usd
