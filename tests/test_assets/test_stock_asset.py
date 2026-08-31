from decimal import Decimal
from domain.assets.stock import Stock
from market_data_provider import MarketDataProvider

from unittest.mock import patch

def test_total_stock_value_from_currency():
    quantity = Decimal("10")
    stock_price = Decimal("150.00")
    pln_rate = Decimal("4.00")

    expected_total_value_pln = quantity * stock_price * pln_rate
    stock = Stock(name="Daily Prophet", currency="KNU", quantity=quantity, ticker="DP")

    with (
        patch.object(MarketDataProvider, "get_stock_price", return_value=stock_price) as mock_get_price,
        patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=pln_rate) as mock_get_rate
    ):
            assert stock.total_value_pln == expected_total_value_pln
            assert stock.unit_price_in_currency == stock_price
            assert stock.currency == "KNU"

    mock_get_rate.assert_called_once_with("KNU")

def test_zero_stock():
    quantity = Decimal(0)
    stock_price = Decimal("150.00")
    pln_rate = Decimal("4.00")

    stock = Stock(name="Daily Prophet", currency="KNU", quantity=quantity, ticker="DP")

    with (
        patch.object(MarketDataProvider, "get_stock_price", return_value=stock_price) as mock_get_price,
        patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=pln_rate) as mock_get_rate
    ):
            assert stock.total_value_pln == Decimal(0)
            assert stock.unit_price_in_currency == stock_price
            assert stock.currency == "KNU"

    mock_get_rate.assert_called_once_with("KNU")

def test_stock_asset_string_representation():
    name = "Gringgotts Stock"
    quantity = Decimal("100")
    currency = "PLN"
    ticker = "WSE:DP"
    stock_price = Decimal("150.00")
    with (
        patch.object(MarketDataProvider, "get_stock_price", return_value=stock_price) as mock_get_price,
    ):
        stock = Stock(name=name, currency=currency, quantity=quantity, ticker=ticker)
        expected_str = f"{name}: {stock.total_value_pln:.2f} {currency}\t\t{ticker} ({quantity:.2f}x{stock.unit_price_in_currency:.2f} [{currency}])"
        assert str(stock) == expected_str