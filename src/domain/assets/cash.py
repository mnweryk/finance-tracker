from functools import cached_property

from .asset import Asset
from  market_data_provider import MarketDataProvider

from decimal import Decimal

class Cash(Asset):
    """Cash holding valued at one unit of its currency per unit held."""

    def __init__(self, name: str, currency: str, quantity: Decimal) -> None:
        super().__init__(name, currency, quantity)
        self.asset_type = "Cash"

    @cached_property
    def unit_price_in_currency(self) -> Decimal:
        """Return the fixed unit price of cash.

        Returns:
            Decimal: Always equal to one.
        """
        return Decimal("1.0")

    @cached_property
    @MarketDataProvider.convert_to_pln
    def total_value_pln(self) -> Decimal:
        """Return the cash quantity converted from its currency to PLN.

        Returns:
            Decimal: Cash value in PLN.
        """
        return self.quantity