import pytest
from decimal import Decimal
from unittest.mock import patch

from market_data_provider import MarketDataProvider

class DummyAsset:
    def __init__(self, currency):
        self.currency = currency

    @MarketDataProvider.convert_to_pln
    def value(self):
        return Decimal("100")

def test_convert_to_pln():
    asset = DummyAsset("USD")

    with patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=Decimal("4.00"),):
        result = asset.value()

    assert result == Decimal("400.00")