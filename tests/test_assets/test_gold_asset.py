from decimal import Decimal
from domain.assets.gold import Gold
from market_data_provider import MarketDataProvider

from unittest.mock import patch

def test_total_gold_value_from_currency():
    quantity = Decimal("2")
    gold_price = Decimal("30000.00")
    pln_rate = Decimal("1.00")  # Gold is forced to PLN, so the conversion rate is 1

    expected_total_value_pln = quantity * gold_price * pln_rate
    gold = Gold(name="Magic Gold", currency="KNU", quantity=quantity, ticker="XAU")

    with (patch.object(MarketDataProvider, "get_gold_price_pln", return_value=gold_price) as mock_get_price):
        assert gold.total_value_pln == expected_total_value_pln
        assert gold.unit_price_in_currency == gold_price
        assert gold.currency == "PLN"  # Ensure currency is forced to PLN


def test_zero_gold():
    quantity = Decimal(0)
    gold_price = Decimal("30000.00")
    
    gold = Gold(name="Weasley's Gold", currency="KNU", quantity=quantity, ticker="XAU")

    with patch.object(MarketDataProvider, "get_gold_price_pln", return_value=gold_price) as mock_get_price:
        assert gold.total_value_pln == Decimal(0)
        assert gold.unit_price_in_currency == gold_price
        assert gold.currency == "PLN"  # Ensure currency is forced to PLN

def test_gold_asset_string_representation():
    name = "Potter's Gold"
    quantity = Decimal("100")
    currency = "PLN"
    ticker = "XAU"
    gold = Gold(name=name, currency=currency, quantity=quantity, ticker=ticker)
    expected_str = f"{name}: {gold.total_value_pln:.2f} {currency}\t\t{ticker} ({quantity:.2f}x{gold.unit_price_in_currency:.2f} [{currency}])"
    assert str(gold) == expected_str