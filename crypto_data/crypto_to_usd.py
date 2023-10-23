from datetime import datetime

class CryptoToUsd:
    def __init__(self, client, eth_to_usd_cache):
        self.client = client
        self.eth_to_usd_cache = eth_to_usd_cache

    def get_crypto_to_usd(self, crypto: str, timestamp: datetime) -> float:
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
