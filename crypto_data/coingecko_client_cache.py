import requests
from datetime import datetime, timezone, timedelta
from typing import Tuple
from requests.exceptions import HTTPError
from time import sleep
import bisect

class CoinGeckoClientWithCache:
    """
    Client for fetching USD values for ETH at given timestamps.

    This class provides an interface to retrieve USD values for ETH based on specified timestamps. 
    Ideally, in a prod environment it would retrieve this data from a prepopulated database using a SQL query, e.g.:
    'SELECT price from eth_to_usd WHERE {timestamp} <= timestamp ORDER BY timestamp DESC LIMIT 1'.
    
    In lack of a database, a local in-memory cache is used that gets built on the fly,
    as more (timestamp, price) pairs are retrieved from CoinGecko API calls.

    The approximate price returned for a transaction will be the last known price before the transaction timestamp.
    Which depending on the transaction age can be up to 5 minutes, 1 hour or 1 day before.

    The primary purpose of using a local cache is to minimize API calls to
    CoinGecko and improve the efficiency of data retrieval.

    Attributes:
        cache (dict): A dictionary storing timestamp-price pairs, serving as a local cache.

    Usage:
        client = CoinGeckoClientWithCache()
        usd_price = client.get('ethereum', some_timestamp)
    """

    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        self.cache = {}
        self.sorted_timestamps = []

    def get(self, crypto: str, timestamp: datetime) -> float:

        pos = bisect.bisect_left(self.sorted_timestamps, timestamp)

        # If the exact timestamp is found in cache
        if pos < len(self.sorted_timestamps) and self.sorted_timestamps[pos] == timestamp:
            return self.cache[timestamp]

        # If a lower timestamp is found in cache
        elif pos > 0:
            return self.cache[self.sorted_timestamps[pos-1]]
        
        # If not found in cache, fetch data from CoinGecko
        from_timestamp, to_timestamp = self._get_time_range(timestamp)
        new_data = self._fetch_data_from_coingecko(crypto, from_timestamp, to_timestamp)
        
        # Update cache and sorted timestamps list
        for key, value in new_data.items():
            utc_timestamp = key.replace(tzinfo=timezone.utc)
            bisect.insort_left(self.sorted_timestamps, utc_timestamp)
            self.cache[utc_timestamp] = value
            
        # Try retrieving the value again from cache after update
        pos = bisect.bisect_left(self.sorted_timestamps, timestamp)
        if pos < len(self.sorted_timestamps) and self.sorted_timestamps[pos] == timestamp:
            return self.cache[timestamp]
        elif pos > 0:
            return self.cache[self.sorted_timestamps[pos-1]]        
        
        return None  # If value is still not found after the update 

    def _fetch_data_from_coingecko(self, crypto: str, from_timestamp: datetime, to_timestamp: datetime) -> dict:
        """
        Fetch data from CoinGecko between the given timestamps.

        Args:
            crypto (str): The cryptocurrency to query for, e.g., 'ethereum'.
            from_timestamp (datetime): The start timestamp.
            to_timestamp (datetime): The end timestamp.

        Returns:
            dict: Dictionary containing the timestamp-price pairs.
        """
        # Convert datetime to UNIX timestamp
        from_unix_timestamp = int(from_timestamp.timestamp())
        to_unix_timestamp = int(to_timestamp.timestamp())
        
        endpoint = f"{self.BASE_URL}/coins/{crypto}/market_chart/range?vs_currency=usd&from={from_unix_timestamp}&to={to_unix_timestamp}"

        retries = 3
        while retries > 0:
            try:
                response = requests.get(endpoint)
                response.raise_for_status()
                prices = response.json().get('prices', [])
                
                # Convert list of lists into a dictionary with datetime objects in seconds as keys
                return {datetime.utcfromtimestamp(price[0] / 1000): price[1] for price in prices}
                
            except HTTPError as e:
                # Check if it's a rate limit error
                if e.response.status_code == 429:
                    print("[CoinGeckoClientWithCache] Rate limit hit. Waiting for 60 seconds before retrying...")
                    sleep(60)
                    retries -= 1
                else:
                    print(f"[CoinGeckoClientWithCache] An unexpected HTTP error occurred when calling {endpoint}:\n{e}")
                    raise e

            except Exception as e:
                print(f"[CoinGeckoClientWithCache] An unexpected error occurred when calling {endpoint}:\n{e}")
                raise e  
        
        return {}

    def _get_time_range(self, timestamp: datetime):
        # Data granularity for coingecko api is automatic (cannot be adjusted)
            # 1 day from current time = 5 minute interval data
            # 2 - 90 days of date range = hourly data
            # above 90 days of date range = daily data (00:00 UTC)
        # Compute the api search interval start based on how old the timestamp we're querying for is.
        # Since we want to return multiple values to populate our cache and reduce the number of api calls,
        # we add an extra buffer (1 day, 30 days, 365 days) to the interval endpoints depending on the timestamp age.
        
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc)

        if timestamp > current_time:
            raise ValueError("The given timestamp is in the future!")

        days_diff = (current_time - timestamp).days
        
        if days_diff <= 1:
            return timestamp - timedelta(days=1), min(current_time, timestamp + timedelta(days=1))
        elif 1 < days_diff <= 90:
            return timestamp - timedelta(days=30), min(current_time, timestamp + timedelta(days=30))
        else:
            return timestamp - timedelta(days=365), min(current_time, timestamp + timedelta(days=365))
        