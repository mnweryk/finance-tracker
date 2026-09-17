from functools import cached_property

from .asset import Asset
from  market_data_provider import MarketDataProvider

from decimal import Decimal

class Gold(Asset):
    """Gold holding priced through the NBP gold price endpoint."""

    def __init__(self, name: str, currency: str, quantity: Decimal, ticker: str) -> None:
        super().__init__(name, currency, quantity, ticker)
        self.asset_type = "Gold"
        # Currently as market data provider only provides gold price in PLN, we set currency to PLN
        self.currency = "PLN"

    @cached_property
    def unit_price_in_currency(self) -> Decimal:
        """Return the current gold price supplied by the market data provider.

        Returns:
            Decimal: Gold price in PLN per unit returned by the provider.
        """
        return MarketDataProvider.get_gold_price_pln()

    @cached_property
    @MarketDataProvider.convert_to_pln
    def total_value_pln(self) -> Decimal:
        """Return the gold holding value converted to PLN.

        Returns:
            Decimal: Total gold value in PLN.
        """
        return self.quantity*self.unit_price_in_currency