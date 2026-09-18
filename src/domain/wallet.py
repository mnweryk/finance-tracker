from collections import defaultdict
import logging

from decimal import Decimal

from .portfolio import Portfolio
from .assets.asset import Asset

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Wallet:
    """Collection of portfolios representing the user's holdings."""

    def __init__(self, name: str = None) -> None:
        self.portfolios: list[Portfolio] = []
        self.name = name if name else "My Wallet"

    def __str__(self) -> str:
        return self.get_wallet_summary_by_asset_type()

    def add_portfolio(self, portfolio_name: str) -> None:
        """Add a portfolio with the given name without duplicate checking."""
        self.portfolios.append(Portfolio(portfolio_name))

    def get_portfolios(self) -> list[Portfolio]:
        """Return the wallet's mutable list of portfolios.

        Returns:
            list[Portfolio]: The wallet's internal portfolio list.
        """
        return self.portfolios

    def add_asset_to_portfolio(self, portfolio_name: str, holding: Asset) -> None:
        """Add an asset to a named portfolio.

        Raises:
            ValueError: If no portfolio has the requested name.
        """
        for portfolio in self.portfolios:
            if portfolio.name == portfolio_name:
                portfolio.add_asset(holding)
                return
        raise ValueError(f"Portfolio with name '{portfolio_name}' not found.")

    def get_total_value_pln(self) -> Decimal:
        """Return the sum of all portfolio values in PLN.

        Returns:
            Decimal: Total wallet value in PLN.
        """
        total_value = Decimal(0)
        for portfolio in self.portfolios:
            total_value += portfolio.get_total_value_pln()
        return total_value

    def print_wallet_portfolios(self) -> str:
        """Return a text summary of portfolios and the total wallet value.

        Returns:
            str: Formatted wallet summary.
        """
        summary = "Wallet Summary:\n********\n"
        for portfolio in self.portfolios:
            summary += f"{portfolio}\n\n"
        summary += f"Total Wallet Value: {self.get_total_value_pln():.2f} PLN\n\n"
        return summary

    def get_wallet_summary_by_asset_type(self) -> str:
        """Return a text summary grouping assets by their asset type.

        Returns:
            str: Formatted summary grouped by asset type.
        """
        assets = self.get_wallet_by_asset_type()
        summary = f"Wallet Summary by Asset Type:\t\ttotal: {self.get_total_value_pln():.2f} PLN\n********\n"
        for asset_type, asset_list in assets.items():
            summary += f"{asset_type}:\n"
            for asset in asset_list:
                summary += f"  {asset}\n"
        return summary

    def get_wallet_by_asset_type(self) -> dict[str, list[Asset]]:
        """Return a new mapping of asset types to the assets of each type.

        Returns:
            dict[str, list[Asset]]: Assets grouped by their type.
        """
        assets: defaultdict[str, list[Asset]] = defaultdict(list)

        for portfolio in self.portfolios:
            for asset in portfolio.assets:
                assets[asset.asset_type].append(asset)

        return dict(assets)
