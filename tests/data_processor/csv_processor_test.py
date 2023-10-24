import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, call

from data_processor import CsvProcessor, RawTransaction

# Sample mock data
SAMPLE_TRANSACTION = {
    'hash': 'sample_hash',
    'nonce': 123,
    'block_hash': 'sample_block_hash',
    'block_number': 123456,
    'transaction_index': 1,
    'from_address': 'sample_from',
    'to_address': 'sample_to',
    'value': 1000000,
    'gas': 21000,
    'gas_price': 1000000000,
    'block_timestamp': '2022-01-01T00:00:00Z',
    'max_fee_per_gas': None,
    'max_priority_fee_per_gas': None,
    'transaction_type': 1,
    'receipts_cumulative_gas_used': 2000000,
    'receipts_gas_used': 2000000,
    'receipts_contract_address': None,
    'receipts_root': None,
    'receipts_status': 1,
    'receipts_effective_gas_price': 1000000000,
}

SAMPLE_ROW = dict(SAMPLE_TRANSACTION)


def mock_csv_stream(*rows):
    for row in rows:
        yield row

@pytest.fixture
def mock_crypto_to_usd_instance():
    instance = Mock()
    instance.get.return_value = 3000  # mock value for ETH to USD
    return instance

@pytest.fixture
def mock_db_repository():
    return Mock()

@pytest.fixture
def csv_processor(mock_crypto_to_usd_instance, mock_db_repository):
    return CsvProcessor(mock_crypto_to_usd_instance, mock_db_repository)

def test_csv_processor_process_valid_transaction(csv_processor):
    with patch.object(csv_processor, 'csv_stream', return_value=mock_csv_stream(SAMPLE_ROW)):
        csv_processor.process('sample.csv')
        csv_processor.db_repository.create.assert_called_once()

def test_csv_processor_process_validation_error(csv_processor):
    invalid_transaction = dict(SAMPLE_ROW)
    invalid_transaction['hash'] = None  # invalid data to trigger ValidationError

    with patch.object(csv_processor, 'csv_stream', return_value=mock_csv_stream(invalid_transaction)):
        csv_processor.process('sample.csv')
        csv_processor.db_repository.create.assert_not_called()

def test_csv_processor_process_generic_error(csv_processor):
    with patch.object(csv_processor, 'csv_stream', side_effect=Exception("Generic error")):
        with pytest.raises(Exception, match="Generic error"):
            csv_processor.process('sample.csv')

def test_compute_gas_cost_in_usd(csv_processor):
    raw_transaction = RawTransaction(**SAMPLE_TRANSACTION)
    result = csv_processor.compute_gas_cost_in_usd(raw_transaction)
    assert result == 6  # Given the mock values: 2 (gas in eth) * 3000 (eth to usd mock value)
