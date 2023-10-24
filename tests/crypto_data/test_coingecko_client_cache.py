import pytest
from datetime import datetime, timezone, timedelta

from crypto_data import CoinGeckoClientWithCache

# Mocking the response from CoinGecko to avoid real API calls
@pytest.fixture
def mock_coingecko_response(monkeypatch):
    def mock_fetch_data_from_coingecko(*args, **kwargs):
        return {
            datetime.utcfromtimestamp(1640995200).replace(tzinfo=timezone.utc): 100.0,
            datetime.utcfromtimestamp(1641081600).replace(tzinfo=timezone.utc): 200.0
        }

    monkeypatch.setattr(CoinGeckoClientWithCache, "_fetch_data_from_coingecko", mock_fetch_data_from_coingecko)

def test_get_existing_timestamp(mock_coingecko_response):
    client = CoinGeckoClientWithCache()
    timestamp = datetime.utcfromtimestamp(1640995200).replace(tzinfo=timezone.utc)
    assert client.get('ethereum', timestamp) == 100.0

def test_get_between_existing_timestamps(mock_coingecko_response):
    client = CoinGeckoClientWithCache()
    timestamp = datetime.utcfromtimestamp(1640995200).replace(tzinfo=timezone.utc)  # A timestamp between the two mock timestamps
    assert client.get('ethereum', timestamp) == 100.0  # Should return the value of the closest available timestamp before the

def test_get_future_timestamp(mock_coingecko_response):
    client = CoinGeckoClientWithCache()
    future_timestamp = datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=1)
    with pytest.raises(ValueError, match="The given timestamp is in the future!"):
        client.get('ethereum', future_timestamp)
