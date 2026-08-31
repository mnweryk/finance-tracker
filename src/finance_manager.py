import tomllib
from pathlib import Path
import logging

from domain.assets.asset_factory import AssetFactory
from domain.wallet import Wallet

from google_sheets_data.config import GoogleSheetsConfig
from google_sheets_data.holdings_parser import GoogleSheetsHoldingParser
from google_sheets_data.row_dto import GoogleSheetsRowDTO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.toml"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FinanceManager:
    """Build a wallet from holdings loaded from Google Sheets."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Load configuration and create an empty wallet.

        Args:
            config_path: Optional path to ``config.toml``. Defaults to the project config.

        Raises:
            FileNotFoundError: If the configuration file is missing.
            ValueError: If required Google Sheets configuration fields are missing.
        """

        self._config: GoogleSheetsConfig = self.load_config(config_path)
        self.wallet: Wallet = Wallet()


    def load_config(self, config_path: Path | None = None) -> GoogleSheetsConfig:
        """Load Google Sheets configuration from a TOML file.

        Args:
            config_path: Optional TOML configuration path. Defaults to the project config.

        Returns:
            GoogleSheetsConfig: Parsed Google Sheets configuration.

        Raises:
            FileNotFoundError: If the configuration file is missing.
            ValueError: If required Google Sheets fields are missing.
        """
        config_file = config_path or DEFAULT_CONFIG_PATH
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found at '{config_file}'. "
            )

        with config_file.open("rb") as config_handle:
            config = tomllib.load(config_handle)

        required_fields = ["credentials_path", "spreadsheet_id", "worksheets"]
        if not all(field in config.get("google_sheets", {}) for field in required_fields):
            raise ValueError(
                f"Config file '{config_file}' is missing required fields. "
                f"Please ensure that 'credentials_path', 'spreadsheet_id', and 'worksheets' are present."
            )

        return GoogleSheetsConfig(**config["google_sheets"])


    def load_sheets_data(self) -> list[GoogleSheetsRowDTO]:
        """Load portfolio holdings from configured Google Sheets worksheets.

        Returns:
            list[GoogleSheetsRowDTO]: Parsed portfolio holding data.

        Raises:
            FileNotFoundError: If the credentials file is missing.
            Exceptions raised while authenticating or fetching Google Sheets data.
        """
        if not Path(self._config.credentials_path).exists():
            raise FileNotFoundError(
                f"Google credentials file not found at '{self._config.credentials_path}'. "
                f"Please verify that your service account JSON key is placed in {self._config.credentials_path}"
            )

        return GoogleSheetsHoldingParser(self._config).spreadsheet_dto


    def build_wallet(self) -> None:
        """Build the wallet from parsed holdings and add missing portfolios.

        The method mutates ``self.wallet`` and does not reset it before adding data.

        Raises:
            ValueError: If a holding contains an unsupported asset type.
            FileNotFoundError: If the Google credentials file is missing.
        """
        sheet_dtos = self.load_sheets_data()
        for dto in sheet_dtos:
            kwargs = {
                "asset_type": dto.asset_type,
                "name": dto.name,
                "currency": dto.currency,
                "quantity": dto.quantity
            }
            if dto.ticker is not None:
                # Do not include ticker in kwargs if it's None to avoid passing it to AssetFactory.create
                kwargs["ticker"] = dto.ticker

            asset = AssetFactory.create(**kwargs)
            if dto.portfolio_name not in [portfolio.name for portfolio in self.wallet.get_portfolios()]:
                self.wallet.add_portfolio(portfolio_name=dto.portfolio_name)

            self.wallet.add_asset_to_portfolio(dto.portfolio_name, asset)



if __name__ == "__main__":
    manager = FinanceManager()
    manager.build_wallet()
    print(manager.wallet)
    print('\n\n')
    print(manager.wallet.print_wallet_portfolios())