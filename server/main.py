import argparse
import uvicorn
from fastapi import FastAPI
from database import init_db, SqlRepository
from server.routes import get_api_router
from crypto_data import CoinGeckoClientWithCache, CryptoToUsd
from data_processor import CsvProcessor

app = FastAPI()

repository = SqlRepository()

app.include_router(get_api_router(repository))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--process_csv', dest='process_csv', action='store_true', 
        help="Process the CSV file and populate the database before starting the server")
    args = parser.parse_args()

    init_db()

    if args.process_csv:
        coin_gecko_client = CoinGeckoClientWithCache()
        crypto_to_usd = CryptoToUsd(client=coin_gecko_client, eth_to_usd_cache={})
        csv_processor = CsvProcessor(crypto_to_usd_instance=crypto_to_usd, db_repository=repository)        
        csv_processor.process(file_path="ethereum_txs.csv")

    uvicorn.run(app, host="0.0.0.0", port=8000)
