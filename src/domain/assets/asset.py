from decimal import Decimal
from abc import ABC, abstractmethod
from functools import cached_property


class Asset(ABC):
    """Base class for assets held in a portfolio."""

    def __init__(self, name: str, currency: str, quantity: Decimal, ticker: str | None = None) -> None:
        """Initialize an asset with its identifying and holding data.

        Args:
            name: Human-readable asset name.
            currency: Currency in which the asset is valued.
            quantity: Number of units held.
            ticker: Optional market ticker.
        """
        self.name = name
        self.ticker = ticker
        self.currency = currency
        self.quantity = quantity
        self.asset_type = ""

    def __str__(self) -> str:
        """Return a summary containing the PLN value and unit valuation."""
        summary = f"{self.name}: {self.total_value_pln:.2f} PLN\t\t"
        summary += f"{self.ticker} " if self.ticker else ""
        summary += f"({self.quantity:.2f}x{self.unit_price_in_currency:.2f} [{self.currency}])"
        return summary


    @cached_property
    @abstractmethod
    def unit_price_in_currency(self) -> Decimal:
        """Return the price of one asset unit in its valuation currency.

        Returns:
            Decimal: Unit price in the asset's valuation currency.
        """
        pass


    @cached_property
    @abstractmethod
    def total_value_pln(self) -> Decimal:
        """Return the total holding value converted to PLN when necessary.

        Returns:
            Decimal: Total value of the holding in PLN.
        """
        pass