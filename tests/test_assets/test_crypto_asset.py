from decimal import Decimal
from domain.assets.crypto import Crypto
from market_data_provider import MarketDataProvider

from unittest.mock import patch

def test_total_crypto_value_from_currency():
    quantity=Decimal("2")
    crypto_price=Decimal("30000.00")
    knu_to_pln_rate=Decimal("2")
    expected_total_value_pln = quantity * crypto_price * knu_to_pln_rate

    crypto = Crypto(name="Magic Bitcoin", currency="KNU", quantity=quantity, ticker="BTC")

    with (
        patch.object(MarketDataProvider, "get_crypto_price", return_value=crypto_price) as mock_get_price,
        patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=knu_to_pln_rate) as mock_convert
    ):
        assert crypto.total_value_pln == expected_total_value_pln
        assert crypto.unit_price_in_currency == crypto_price

def test_zero_crypto():
    crypto = Crypto(name="Weasley's Bitcoin", currency="KNU", quantity=Decimal(0), ticker="BTC")

    with (
        patch.object(MarketDataProvider, "get_crypto_price", return_value=Decimal("30000.00")) as mock_get_price,
        patch.object(MarketDataProvider, "get_currency_pln_rate", return_value=Decimal("2")) as mock_convert
    ):
        assert crypto.total_value_pln == Decimal(0)
        assert crypto.unit_price_in_currency == Decimal("30000.00")


def test_crypto_asset_string_representation():
    name = "Potter's Crypto"
    quantity = Decimal("100")
    currency = "PLN"
    ticker = "BTC"
    crypto = Crypto(name=name, currency=currency, quantity=quantity, ticker=ticker)
    expected_str = f"{name}: {crypto.total_value_pln:.2f} {currency}\t\t{ticker} ({quantity:.2f}x{crypto.unit_price_in_currency:.2f} [{currency}])"
    assert str(crypto) == expected_str