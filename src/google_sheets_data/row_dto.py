from dataclasses import dataclass
from decimal import Decimal


@dataclass
class GoogleSheetsRowDTO:
    portfolio_name: str
    name: str
    quantity: Decimal
    currency: str
    ticker: str | None = None

