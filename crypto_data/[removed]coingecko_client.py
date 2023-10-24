import requests
from datetime import datetime, timezone, timedelta
from typing import Tuple
from requests.exceptions import HTTPError
from time import sleep

"""
This was the initial CoinGeckoClient that I implemented.
It calls the  API to only get the last price and timestamp before the transaction time.

While it is simpler and more readable than the one with a cache, it is also inefficient.
The reason for this is that for old transaction timestamp the api granularity is 1 hour or 1 day (for 90+ days).
Given the block length is 12 seconds, it means that in an hour we'll have 300 transactions mapping to the same aprox timestamp,
and in a day we'll have 7200, resulting in too many redundant API calls.

It's better to call the API for a longer period of time, store the timestamps in a database/cache, and use it when getting the approximate price.
This is what CoinGeckoClientWithCache implements. 
"""
class CoinGeckoClient:
    
    BASE_URL = "https://api.coingecko.com/api/v3"

    @classmethod
    def get(cls, crypto: str, timestamp: datetime) -> float:
        # Get the api search interval
        from_unix_timestamp = CoinGeckoClient._get_start_timestamp_range(timestamp)
        to_unix_timestamp = int(timestamp.timestamp())

        # Construct the API endpoint
        endpoint = f"{cls.BASE_URL}/coins/{crypto}/market_chart/range?vs_currency=usd&from={from_unix_timestamp}&to={to_unix_timestamp}"

        retries = 3
        while retries > 0:
            try:
                response = requests.get(endpoint)
                response.raise_for_status()

                # Get the last price data known before the provided timestamp
                prices_array = response.json()["prices"]
                price_data = prices_array[-1][1]

                return price_data

            except HTTPError as e:
                # Check if it's a rate limit error
                if e.response.status_code == 429:
                    print("[CoinGeckoClient] Rate limit hit. Waiting for 60 seconds before retrying...")
                    sleep(60)
                    retries -= 1
                else:
                    raise e

            except Exception as ex:
                print(f"[CoinGeckoClient] An unexpected error occurred when calling {endpoint}:\n{ex}")
                raise ex               

    @staticmethod
    def _get_start_timestamp_range(timestamp: datetime) -> int:
        # Data granularity for coingecko api is automatic (cannot be adjusted)
            # 1 day from current time = 5 minute interval data
            # 2 - 90 days of date range = hourly data
            # above 90 days of date range = daily data (00:00 UTC)
        # Compute the api search interval start based on how old the timestamp we're querying for is

        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)

        if timestamp > current_time:
            raise ValueError("The given timestamp is in the future!")
        
        delta_90_days = timedelta(days=90)
        delta_1_day = timedelta(days=1)
        delta_1_hour = timedelta(hours=1)
        delta_5_minutes = timedelta(minutes=5)

        if timestamp > current_time - delta_1_day:
            return int((timestamp - delta_5_minutes).timestamp())

        elif timestamp > current_time - delta_90_days:
            return int((timestamp - delta_1_hour).timestamp())

        else:
            return int((timestamp - delta_1_day).timestamp())
