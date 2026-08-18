import tomllib
from pathlib import Path
from typing import Any
import logging
from google_sheets_data.config import GoogleSheetsConfig
from google_sheets_data.holdings_parser import GoogleSheetsHoldingParser
from google_sheets_data.row_dto import GoogleSheetsRowDTO

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.toml"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FinanceManager:
    """Orchestrates loading portfolio data from external sources."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Load configuration and initialize sheet fetcher dependencies.    

        Args:
            config_path: Optional path to config.toml. Defaults to config/config.toml in the project root.

        Raises:
            FileNotFoundError: If the config file or credentials JSON file is missing.
        """

        self._config = self.load_config(config_path)


    def load_config(self, config_path: Path | None = None) -> GoogleSheetsConfig:
        """Load configuration from toml file

        Args:
            config_path: path to toml configuration file. If not provided default is taken

        Returns:
            Configuration class object

        Raises: 
            FileNotFoundError: If the config file is missing.
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


    def load_sheets_data(self) -> GoogleSheetsRowDTO:
        """Load portfolio holdings from configured Google Sheets worksheets.

        Returns:
            GoogleSheetsRowDTO: Parsed portfolio holding data.
        """
        if not Path(self._config.credentials_path).exists():
            raise FileNotFoundError(
                f"Google credentials file not found at '{self._config.credentials_path}'. "
                f"Please verify that your service account JSON key is placed in {self._config.credentials_path}"
            )

        return GoogleSheetsHoldingParser(self._config).create_dtos()


if __name__ == "__main__":
    manager = FinanceManager()
    worksheet_data = manager.load_sheets_data()

    print(worksheet_data)