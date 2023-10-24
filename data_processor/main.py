from crypto_data.coingecko_client import CoinGeckoClient
from crypto_data.coingecko_client_cached import CoinGeckoClientWithCache
from crypto_data.crypto_to_usd import CryptoToUsd
from data_processor.csv_processor import CsvProcessor
from database.in_memory_repository import InMemoryRepository
from database.sql_repository import SqlRepository
from models.processed_transaction import ProcessedTransaction 
from database import database

database.init_db()

# Instantiate the required components
coin_gecko_client = CoinGeckoClient()
coin_gecko_client_cached = CoinGeckoClientWithCache()

crypto_to_usd = CryptoToUsd(client=coin_gecko_client_cached, eth_to_usd_cache={})
#repository = InMemoryRepository()
# repository.load('processed_transactions.pk1')
repository = SqlRepository()
csv_processor = CsvProcessor(crypto_to_usd_instance=crypto_to_usd, db_repository=repository)

# # Process the CSV file
csv_processor.process_csv_stream(file_path="ethereum_txs.csv")
#repository.save('processed_transactions.pk1')

# Print the details of transactions with the given hashes
transaction_hashes = [
    "0xc055b65e39c15e1bc90cb4ccb2daac6b59c02ec1aa6c4216276054b4f31ed90a",
    "0xbd6bba5229fdbe5a3e68ef358d8eb3ae5e85e3c1677eda337da80daff55ae976",
    "0xf8e3668111b0162d5717d54b2fe6ccba044429e5ba706c61b2ff153ac218ffbb"
]

for tx_hash in transaction_hashes:
    tx = repository.get_by_hash(tx_hash)
    if tx:
        print(tx)
    else:
        print(f"Transaction with hash {tx_hash} not found!")

if __name__ == "__main__":
    # Ensure that the script execution starts here
    pass
