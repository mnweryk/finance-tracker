from pathlib import Path
import argparse
import logging

from dotenv import load_dotenv

from config_reader import ConfigReader
from domain.assets.asset_factory import AssetFactory
from domain.wallet import Wallet

from google_sheets_data.config import GoogleSheetsConfig
from google_sheets_data.holdings_parser import GoogleSheetsHoldingParser
from google_sheets_data.row_dto import GoogleSheetsRowDTO

from db.repository import WalletSnapshotModel, PortfolioSnapshotModel, AssetSnapshotModel
from db.connection import DatabaseConnection
from db.repository import SnapshotRepository

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SECRETS_PATH = PROJECT_ROOT / ".secrets" / "secrets.env"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FinanceManager:
    """Build a wallet from holdings loaded from Google Sheets."""

    def __init__(self, config_path: Path | None = None, skip_database_save: bool = False) -> None:
        """Load configuration and create an empty wallet.

        Args:
            config_path: Optional path to ``config.toml``. Defaults to the project config.

        Raises:
            FileNotFoundError: If the configuration file is missing.
            ValueError: If required configuration fields are missing.
        """
        self.load_secrets()
        self.skip_database_save = skip_database_save
        self._config: ConfigReader = ConfigReader(
            config_path=config_path,
            require_database=not skip_database_save,
        )
        self.wallet: Wallet = Wallet()


    def load_secrets(self, secrets_path: Path | None = None) -> None:
        """Load secrets from a .env file.

        Args:
            secrets_path: Optional path to the .env file. Defaults to the project secrets.
        """
        secrets_path = secrets_path or DEFAULT_SECRETS_PATH
        if secrets_path.exists():
            load_dotenv(dotenv_path=secrets_path)
            logger.debug(f"Secrets loaded from '{secrets_path}'.")
        else:
            logger.debug(f"Secrets file not found at '{secrets_path}'. Skipping loading secrets.")


    def load_sheets_data(self) -> list[GoogleSheetsRowDTO]:
        """Load portfolio holdings from configured Google Sheets worksheets.

        Returns:
            list[GoogleSheetsRowDTO]: Parsed portfolio holding data.

        Raises:
            FileNotFoundError: If the credentials file is missing.
            Exceptions raised while authenticating or fetching Google Sheets data.
        """
        if not Path(self._config.google_config.credentials_path).exists():
            raise FileNotFoundError(
                f"Google credentials file not found at '{self._config.google_config.credentials_path}'. "
                f"Please verify that your service account JSON key is placed in {self._config.google_config.credentials_path}"
            )

        return GoogleSheetsHoldingParser(self._config.google_config).spreadsheet_dto


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
    parser = argparse.ArgumentParser(description="Load holdings and optionally save a database snapshot.")
    parser.add_argument(
        "--skip_database_save",
        action="store_true",
        help="Load and display holdings without saving a snapshot to the database.",
    )
    args = parser.parse_args()

    manager = FinanceManager(skip_database_save=args.skip_database_save)
    manager.build_wallet()
    print(manager.wallet)
    print('\n\n')
    print(manager.wallet.print_wallet_portfolios())

    if not manager.skip_database_save:
        db_connection = DatabaseConnection(manager._config.db_config)

        with db_connection.get_session() as session:
            db_snapshot_repository = SnapshotRepository(session=session)
            db_snapshot_repository.save_snapshot(wallet=manager.wallet)