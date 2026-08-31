from decimal import Decimal

import pytest
from domain.assets.cash import Cash
from market_data_provider import MarketDataProvider

from unittest.mock import patch

def test_total_cash_value_from_currency():
    cash = Cash(name="Knuts Cash", currency="KNU", quantity=Decimal("100"))

    with patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=Decimal("4.00")) as mock_get_rate:
        assert cash.total_value_pln == Decimal("400.00")

    mock_get_rate.assert_called_once_with("KNU")
    assert cash.unit_price_in_currency == Decimal(1)

def test_total_cash_value_from_pln():
    cash = Cash(name="Muggles money", currency="PLN", quantity=Decimal("111"))

    assert cash.total_value_pln == Decimal("111")
    assert cash.unit_price_in_currency == Decimal(1)

def test_zero_cash():
    cash = Cash(name="Weasleys money", currency="KNU", quantity=Decimal(0))

    with patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=Decimal("4.00")) as mock_get_rate:
        assert cash.total_value_pln == Decimal(0)
    assert cash.unit_price_in_currency == Decimal(1)

def test_initialization_with_ticker():
    with pytest.raises(TypeError):
        Cash(name="Galleons Cash", currency="KNU", quantity=Decimal("50"), ticker="GOLD")

def test_cash_asset_string_representation():
    name = "Potter's Money"
    quantity = Decimal("100")
    currency = "PLN"
    cash = Cash(name=name, currency=currency, quantity=quantity)
    expected_str = f"{name}: {cash.total_value_pln:.2f} {currency}\t\t({quantity:.2f}x{cash.unit_price_in_currency:.2f} [{currency}])"
    assert str(cash) == expected_str