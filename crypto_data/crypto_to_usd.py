from datetime import datetime

class CryptoToUsd:
    """
    A utility class for converting cryptocurrency values to USD using a cache and an external client.

    Args:
        client: An external client for fetching cryptocurrency conversion rates.
        eth_to_usd_cache: A cache dictionary for storing Ethereum to USD conversion rates.

    Methods:
        get(crypto: str, timestamp: datetime) -> float:
            Get the value of a cryptocurrency in USD at a specific timestamp.

    Raises:
        ValueError: If the provided cryptocurrency is not supported.
    """

    def __init__(self, client, eth_to_usd_cache):
        self.client = client
        self.eth_to_usd_cache = eth_to_usd_cache

    def get(self, crypto: str, timestamp: datetime) -> float:
        """
        Get the value of a cryptocurrency in USD at a specific timestamp.

        Args:
            crypto (str): The cryptocurrency to convert (e.g., 'ethereum').
            timestamp (datetime): The timestamp at which to fetch the conversion rate.

        Returns:
            float: The value of the cryptocurrency in USD at the specified timestamp.

        Raises:
            ValueError: If the provided cryptocurrency is not supported.
        """        
        if crypto != 'ethereum':
            raise ValueError(f"Cryptocurrency {crypto} not supported")

        cache_key = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        # Check in the cache first
        if cache_key in self.eth_to_usd_cache:
            return self.eth_to_usd_cache[cache_key]

        # If not in the cache, fetch using the injected client
        print(f"[CryptoToUsd] {cache_key} not in the eth_to_usd_cache. Will retrieve it using the http client.")
        usd_value = self.client.get(crypto, timestamp)
        self.eth_to_usd_cache[cache_key] = usd_value

        return usd_value
