from .asset import Asset
from  market_data_provider import MarketDataProvider

from decimal import Decimal

class Bond(Asset):
    """Bond holding with a temporary fixed unit price."""

    def __init__(self, name: str, currency: str, quantity: Decimal, ticker: str) -> None:
        super().__init__(name, currency, quantity, ticker)
        self.asset_type = "Bond"

    @property
    def unit_price_in_currency(self) -> Decimal:
        """Return the placeholder bond price.

        Returns:
            Decimal: Fixed placeholder price of 100.
        """
        # Placeholder implementation; in a real scenario, this would fetch the current market price of the bond.
        return Decimal("100")  # Example fixed price for demonstration purposes.

    @property
    @MarketDataProvider.convert_to_pln
    def total_value_pln(self) -> Decimal:
        """Return the placeholder-priced holding value converted to PLN.

        Returns:
            Decimal: Total bond value in PLN.
        """
        return self.quantity * self.unit_price_in_currency