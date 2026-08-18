import logging
from decimal import Decimal, InvalidOperation

from .config import GoogleSheetsConfig
from .fetcher import GoogleSheetsFetcher
from .row_dto import GoogleSheetsRowDTO


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AssetAttributes:
    NAME = "Name"
    TICKER = "Ticker"
    CURRENCY = "Currency"
    QUANTITY = "Quantity"


class GoogleSheetsHoldingParser:
    def __init__(self, config: GoogleSheetsConfig) -> None:
        self.config = config
        self.spreadsheet_dto = []
        self.create_dtos()

    def create_dtos(self):
        """Creates DTOs for each worksheet in the Google Sheets configuration."""
        for worksheet in self.config.worksheets:
            raw_data = GoogleSheetsFetcher(self.config.credentials_path, self.config.spreadsheet_id).fetch_worksheet(worksheet)
            header_row = raw_data[2]
            portfolios = self.get_portfolios(raw_data[1])
            logger.debug(f"Found portfolios: {portfolios} in worksheet: {worksheet}")

            step = len(header_row) // len(portfolios)
            portfolio_header = header_row[:step]

            column_mapping = {col.strip(): i for i, col in enumerate(portfolio_header) if col.strip() in [AssetAttributes.NAME, AssetAttributes.TICKER, AssetAttributes.CURRENCY, AssetAttributes.QUANTITY]}

            for row in raw_data[3:]:
                dtos = self.parse_row(row, portfolios, step, column_mapping)
                for dto in dtos:
                    self.spreadsheet_dto.append(dto)
                    logger.debug(f"Created DTO: {dto}")
                    print(f"Created DTO: {dto}")

    @staticmethod
    def get_portfolios(raw_data: list):
        """Parses raw data row Google Sheet to obtain list of portoflios

        Args:
            raw_data: list visulising whole Google Sheet header row

        Returns:
            List of portfolio names
        """
        portfolios = []
        portfolios.append(raw_data[0])
        for index, element in enumerate(raw_data):
            try:
                Decimal(element.replace("\xa0", "").replace(" ", "").replace("zł", "").replace(',', '.').replace('%', ''))
                if index < len(raw_data) - 1 and raw_data[index + 1]:
                    portfolios.append(raw_data[index + 1])
            except InvalidOperation:
                logger.debug(f"Failed to parse {element}")
        return portfolios

    def parse_row(self, row: list[str], portfolios: list[str], step: int, column_mapping: dict) -> list[GoogleSheetsRowDTO]:
        """Parses a single row of Google Sheet data into a list of GoogleSheetsRowDTOs.

        Args:
            row: List of cell values from a single row in the Google Sheet.
            portfolios: List of portfolio names corresponding to the columns in the row.
            step: Number of columns per portfolio.
            column_mapping: Mapping of column names to column indices within a portfolio block.

        Returns:
            A list of GoogleSheetsRowDTO objects.
        """
        dtos = []

        for i, portfolio in enumerate(portfolios):
            start = i * step
            portfolio_data = row[start : start + step]

            name_idx = column_mapping.get(AssetAttributes.NAME)
            if name_idx is None or name_idx >= len(portfolio_data):
                continue

            name = portfolio_data[name_idx].strip() if portfolio_data[name_idx] else ""
            if not name:
                continue

            qty_idx = column_mapping.get(AssetAttributes.QUANTITY)
            qty_raw = portfolio_data[qty_idx] if qty_idx is not None and qty_idx < len(portfolio_data) else "0"

            curr_idx = column_mapping.get(AssetAttributes.CURRENCY)
            curr = portfolio_data[curr_idx].strip() if curr_idx is not None and curr_idx < len(portfolio_data) and portfolio_data[curr_idx] else ""

            ticker = None
            if AssetAttributes.TICKER in column_mapping:
                ticker_idx = column_mapping[AssetAttributes.TICKER]
                if ticker_idx < len(portfolio_data) and portfolio_data[ticker_idx]:
                    ticker = portfolio_data[ticker_idx].strip()

            try:
                if "%" in qty_raw:
                    qty = Decimal(qty_raw.replace("\xa0", "").replace(" ", "").replace(",", ".").replace("%", "")) / Decimal("100")
                else:
                    qty = Decimal(qty_raw.replace("\xa0", "").replace(" ", "").replace(",", "."))
            except (ValueError, InvalidOperation):
                qty = Decimal("0")

            dtos.append(GoogleSheetsRowDTO(
                portfolio_name=portfolio,
                name=name,
                quantity=qty,
                currency=curr,
                ticker=ticker
            ))

        return dtos

