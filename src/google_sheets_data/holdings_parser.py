import logging
from decimal import Decimal, InvalidOperation

from .config import GoogleSheetsConfig
from .fetcher import GoogleSheetsFetcher
from .row_dto import GoogleSheetsRowDTO


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AssetAttributes:
    """Column names expected in each worksheet asset block."""

    NAME = "Name"
    TICKER = "Ticker"
    CURRENCY = "Currency"
    QUANTITY = "Quantity"


class GoogleSheetsHoldingParser:
    """Parse Google Sheets worksheets into holding DTOs."""

    def __init__(self, config: GoogleSheetsConfig) -> None:
        """Create a parser and eagerly load all configured worksheet DTOs.

        Args:
            config: Google Sheets credentials, spreadsheet, and worksheet configuration.

        Raises:
            Exceptions raised while authenticating, fetching worksheets, or parsing data.
        """
        self.config: GoogleSheetsConfig = config
        self.spreadsheet_dto: list[GoogleSheetsRowDTO] = self.create_dtos()

    def create_dtos(self) -> list[GoogleSheetsRowDTO]:
        """Create DTOs for each configured worksheet.

        Worksheets are expected to contain portfolio totals at index 1, column headers
        at index 2, and asset rows from index 3 onward. Rows without an asset name are
        skipped, and invalid quantities are converted to ``Decimal("0")``.

        Returns:
            list[GoogleSheetsRowDTO]: Parsed holdings from all configured worksheets.
        """
        dtos: list[GoogleSheetsRowDTO] = []
        for worksheet in self.config.worksheets:
            raw_data = GoogleSheetsFetcher(self.config.credentials_path, self.config.spreadsheet_id).fetch_worksheet(worksheet)
            header_row = raw_data[2]
            portfolios = self.get_portfolios(raw_data[1])
            logger.debug(f"Found portfolios: {portfolios} in worksheet: {worksheet}")

            step = len(header_row) // len(portfolios)
            portfolio_header = header_row[:step]

            column_mapping = {col.strip(): i for i, col in enumerate(portfolio_header) if col.strip() in [AssetAttributes.NAME, AssetAttributes.TICKER, AssetAttributes.CURRENCY, AssetAttributes.QUANTITY]}

            for row in raw_data[3:]:
                row_dtos = self.parse_row(worksheet, row, portfolios, step, column_mapping)
                for dto in row_dtos:
                    dtos.append(dto)

        return dtos

    @staticmethod
    def get_portfolios(raw_data: list[str]) -> list[str]:
        """Extract portfolio names from a worksheet totals row.

        Args:
            raw_data: Cells from the row containing portfolio totals and names.

        Returns:
            list[str]: Portfolio names inferred from the row.
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

    def parse_row(
        self,
        worksheet: str,
        row: list[str],
        portfolios: list[str],
        step: int,
        column_mapping: dict[str, int],
    ) -> list[GoogleSheetsRowDTO]:
        """Parse one worksheet row into one DTO per populated portfolio block.

        Args:
            worksheet: Worksheet name stored in each DTO as ``asset_type``.
            row: Cell values from one worksheet row.
            portfolios: Portfolio names corresponding to column blocks in the row.
            step: Number of columns in each portfolio block.
            column_mapping: Column names mapped to indices within a block.

        Returns:
            list[GoogleSheetsRowDTO]: DTOs for non-empty asset names. Invalid or missing
                quantities are represented by ``Decimal("0")``.
        """
        dtos: list[GoogleSheetsRowDTO] = []

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
                asset_type=worksheet,
                portfolio_name=portfolio,
                name=name,
                quantity=qty,
                currency=curr,
                ticker=ticker
            ))

        return dtos

