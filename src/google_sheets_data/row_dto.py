from dataclasses import dataclass
from decimal import Decimal


@dataclass
class GoogleSheetsRowDTO:
    """Parsed holding data for one asset in one portfolio."""

    asset_type: str
    portfolio_name: str
    name: str
    quantity: Decimal
    currency: str
    ticker: str | None = None

