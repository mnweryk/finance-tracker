from .asset import Asset
from  market_data_provider import MarketDataProvider

from decimal import Decimal

class Stock(Asset):
    """Tradable stock whose price is obtained from the market data provider."""

    def __init__(self, name: str, currency: str, quantity: Decimal, ticker: str) -> None:
        super().__init__(name, currency, quantity, ticker)
        self.asset_type = "Stock"

    @property
    def unit_price_in_currency(self) -> Decimal:
        """Return the current stock price in the stock's trading currency.

        Returns:
            Decimal: Current unit price in the trading currency.
        """
        return Decimal(MarketDataProvider.get_stock_price(self.ticker))

    @property
    @MarketDataProvider.convert_to_pln
    def total_value_pln(self) -> Decimal:
        """Return the holding value after conversion to PLN.

        Returns:
            Decimal: Total stock value in PLN.
        """
        return self.quantity * self.unit_price_in_currency