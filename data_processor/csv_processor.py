from pydantic import ValidationError
import csv
from datetime import datetime
from models.raw_transaction import RawTransaction
from models.processed_transaction import ProcessedTransaction
from database.irepository import IRepository
from crypto_data.crypto_to_usd import CryptoToUsd

class CsvProcessor:

    def __init__(self, crypto_to_usd_instance: CryptoToUsd, db_repository: IRepository):
        self.crypto_to_usd_instance = crypto_to_usd_instance
        self.db_repository = db_repository

    def process_csv_stream(self, file_path: str):
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
        eth_to_usd = self.crypto_to_usd_instance.get_crypto_to_usd('ethereum', transaction.block_timestamp)
        gas_cost_usd = gas_cost_eth * eth_to_usd

        return gas_cost_usd
