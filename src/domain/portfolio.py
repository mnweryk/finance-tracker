import logging

from decimal import Decimal

from .assets.asset import Asset


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Portfolio:
    """Collection of assets belonging to one named portfolio."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.assets: list[Asset] = []

    def __str__(self) -> str:
        return self.portfolio_summary()

    def print_portfolio(self) -> None:
        """Log the portfolio summary at INFO level."""
        logger.info(self.portfolio_summary())

    def portfolio_summary(self) -> str:
        """Return a text summary with the total and each held asset.

        Returns:
            str: Formatted portfolio summary.
        """
        asset_types = list(set([asset.asset_type for asset in self.assets]))
        summary = f"Portfolio: {self.name} - {self.get_total_value_pln():.2f} PLN ({' '.join(asset_types)})\n"
        for asset in self.assets:
            summary += f"{asset}\n"
        return summary

    def get_total_value_pln(self) -> Decimal:
        """Return the sum of all asset values in PLN.

        Returns:
            Decimal: Total portfolio value, or zero for an empty portfolio.
        """
        value = Decimal(0)
        for asset in self.assets:
            value += asset.total_value_pln
        return value

    def add_asset(self, asset: Asset) -> None:
        """Append an asset to the portfolio without deduplication or validation."""
        self.assets.append(asset)