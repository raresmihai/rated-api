import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from crypto_data import CryptoToUsd


def test_invalid_crypto():
    client = Mock()
    eth_to_usd_cache = {}
    crypto_converter = CryptoToUsd(client, eth_to_usd_cache)

    with pytest.raises(ValueError, match="Cryptocurrency bitcoin not supported"):
        crypto_converter.get('bitcoin', datetime.now())

def test_value_from_cache():
    client = Mock()
    timestamp = datetime.now()
    cache_key = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    eth_to_usd_cache = {cache_key: 2500.0}
    crypto_converter = CryptoToUsd(client, eth_to_usd_cache)

    result = crypto_converter.get('ethereum', timestamp)

    assert result == 2500.0
    client.get.assert_not_called()  # Ensure client wasn't called since we fetched from cache

def test_value_from_client():
    timestamp = datetime.now()
    client = Mock()
    client.get.return_value = 3000.0
    eth_to_usd_cache = {}
    crypto_converter = CryptoToUsd(client, eth_to_usd_cache)

    result = crypto_converter.get('ethereum', timestamp)

    client.get.assert_called_once_with('ethereum', timestamp)
    assert result == 3000.0
    assert crypto_converter.eth_to_usd_cache[timestamp.strftime('%Y-%m-%d %H:%M:%S')] == 3000.0

def test_value_updates_cache():
    timestamp = datetime.now()
    client = Mock()
    client.get.return_value = 3000.0
    eth_to_usd_cache = {}
    crypto_converter = CryptoToUsd(client, eth_to_usd_cache)

    # First call, fetch from the client
    crypto_converter.get('ethereum', timestamp)
    assert client.get.call_count == 1

    # Second call, fetch from the cache
    crypto_converter.get('ethereum', timestamp)
    assert client.get.call_count == 1  # Ensure client wasn't called again

def test_cache_does_not_have_partial_dates():
    timestamp = datetime.now()
    client = Mock()
    client.get.return_value = 3000.0
    eth_to_usd_cache = {}
    crypto_converter = CryptoToUsd(client, eth_to_usd_cache)

    crypto_converter.get('ethereum', timestamp)

    # Assert cache doesn't store partial date keys
    partial_date = timestamp.strftime('%Y-%m-%d')
    assert partial_date not in crypto_converter.eth_to_usd_cache
