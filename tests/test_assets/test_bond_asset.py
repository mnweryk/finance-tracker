from decimal import Decimal
from domain.assets.bond import Bond
from market_data_provider import MarketDataProvider

from unittest.mock import patch

def test_total_bond_value_from_currency():
    quantity = Decimal("5")
    bond_price = Decimal("100.00")
    pln_rate = Decimal("4.00")

    expected_total_value_pln = quantity * bond_price * pln_rate
    bond = Bond(name="Ministry of Magic Bond", currency="KNU", quantity=quantity, ticker="MM")

    with (
        patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=pln_rate) as mock_get_rate
    ):
            assert bond.total_value_pln == expected_total_value_pln
            assert bond.unit_price_in_currency == bond_price # Currently hardcoded to 100
            assert bond.currency == "KNU"

    mock_get_rate.assert_called_once_with("KNU")

def test_zero_bond():
    quantity = Decimal(0)
    bond_price = Decimal("100.00")
    pln_rate = Decimal("4.00")

    bond = Bond(name="Ministry of Magic Bond", currency="KNU", quantity=quantity, ticker="MM")

    with (
        patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=pln_rate) as mock_get_rate
    ):
            assert bond.total_value_pln == Decimal(0)
            assert bond.unit_price_in_currency == bond_price # Currently hardcoded to 100
            assert bond.currency == "KNU"

    mock_get_rate.assert_called_once_with("KNU")

def test_bond_asset_string_representation():
    name = "Ministry of Magic Bond"
    quantity = Decimal("5")
    currency = "PLN"
    ticker = "MM"
    bond = Bond(name=name, currency=currency, quantity=quantity, ticker=ticker)
    expected_str = f"{name}: {bond.total_value_pln:.2f} {currency}\t\t{ticker} ({quantity:.2f}x{bond.unit_price_in_currency:.2f} [{currency}])"
    assert str(bond) == expected_str