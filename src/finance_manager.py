import tomllib
from pathlib import Path
from typing import Any

from fetchers.google_sheets import GoogleSheetsFetcher
from config.google_sheets_config import GoogleSheetsConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.toml"


class FinanceManager:
    """Orchestrates loading portfolio data from external sources."""

    def __init__(self, fetcher: GoogleSheetsFetcher | None = None, config_path: Path | None = None) -> None:
        """Load configuration and initialize sheet fetcher dependencies.    

        Args:
            fetcher: Optional pre-configured GoogleSheetsFetcher instance for dependency injection.
            config_path: Optional path to config.toml. Defaults to config/config.toml in the project root.

        Raises:
            FileNotFoundError: If the config file or credentials JSON file is missing.
        """
        config_file = config_path or DEFAULT_CONFIG_PATH
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found at '{config_file}'. "
            )

        with config_file.open("rb") as config_handle:
            config = tomllib.load(config_handle)

        google_sheets_config = GoogleSheetsConfig(**config["google_sheets"])
        self._worksheet_names = google_sheets_config.worksheets

        if not fetcher:
            credentials_path = (
                google_sheets_config.credentials_path
                if Path(google_sheets_config.credentials_path).is_absolute()
                else PROJECT_ROOT / google_sheets_config.credentials_path
            )
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"Google credentials file not found at '{credentials_path}'. "
                    f"Please verify that your service account JSON key is placed in {google_sheets_config.credentials_path}"
                )

            spreadsheet_id = google_sheets_config.spreadsheet_id
            self._google_sheets_fetcher = GoogleSheetsFetcher(
                credentials_path=str(credentials_path),
                spreadsheet_id=spreadsheet_id,
            )
        else:
            self._google_sheets_fetcher = fetcher


    def load_sheets_data(self) -> dict[str, list[list[Any]]]:
        """Load portfolio holdings from configured Google Sheets worksheets.

        Returns:
            Raw worksheet data keyed by worksheet name.
        """
        return self._google_sheets_fetcher.fetch_worksheets(self._worksheet_names)


if __name__ == "__main__":
    manager = FinanceManager()
    worksheet_data = manager.load_sheets_data()

    print(worksheet_data)