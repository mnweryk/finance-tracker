from .asset import Asset
from  market_data_provider import MarketDataProvider

from decimal import Decimal

class Crypto(Asset):
    """Cryptocurrency holding priced in USD through the market data provider."""

    def __init__(self, name: str, currency: str, quantity: Decimal, ticker: str) -> None:
        super().__init__(name, currency, quantity, ticker)
        self.asset_type = "Crypto"

    @property
    def unit_price_in_currency(self) -> Decimal:
        """Return the current cryptocurrency price reported in USD.

        Returns:
            Decimal: Current cryptocurrency price in USD.
        """
        return Decimal(MarketDataProvider.get_crypto_price(self.ticker))

    @property
    @MarketDataProvider.convert_to_pln
    def total_value_pln(self) -> Decimal:
        """Return the cryptocurrency holding value converted to PLN.

        Returns:
            Decimal: Total cryptocurrency value in PLN.
        """
        return self.quantity*self.unit_price_in_currency