import tomllib
from pathlib import Path
from typing import Any

from google_sheets_data.config import GoogleSheetsConfig
from db.db_config import DatabaseConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.toml"


class ConfigReader:
    """Read and validate application configuration for Google Sheets and future DB settings."""

    def __init__(self, config_path: Path | None = None):
        self.google_config: GoogleSheetsConfig | None = None
        self.db_config: DatabaseConfig | None = None
        self.load_config(config_path)

    def load_config(self, config_path: Path | None = None) -> None:
        """Load and populate the reader with config values.

        Args:
            config_path: Optional path to the TOML config file. Defaults to the project
                configuration file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the Google Sheets section is invalid.
        """
        config_file = config_path or DEFAULT_CONFIG_PATH
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found at '{config_file}'.")

        with config_file.open("rb") as config_handle:
            config = tomllib.load(config_handle)

        self.google_config = self.load_google_sheets_config(config)
        self.db_config = self.load_database_config(config)


    def load_google_sheets_config(self, app_config: dict[str, Any]) -> GoogleSheetsConfig:
        """Load and validate the Google Sheets configuration section.

        Args:
            app_config: Pre-loaded application configuration dictionary.

        Returns:
            GoogleSheetsConfig: Parsed and validated Google Sheets configuration.

        Raises:
            ValueError: If the ``[google_sheets]`` section or any required field is missing.
        """
        if app_config is None:
            raise ValueError("Application config is required to load Google Sheets settings.")

        google_sheets_config = app_config.get("google_sheets")
        if not isinstance(google_sheets_config, dict):
            raise ValueError(
                "Config file is missing the '[google_sheets]' section. "
                "Please ensure that the section is present and valid."
            )

        required_fields = ["credentials_path", "spreadsheet_id", "worksheets"]
        missing_fields = [field for field in required_fields if field not in google_sheets_config]
        if missing_fields:
            raise ValueError(
                "Config file is missing required fields. "
                "Please ensure that 'credentials_path', 'spreadsheet_id', and 'worksheets' are present."
            )

        return GoogleSheetsConfig(**google_sheets_config)
    

    def load_database_config(self, app_config: dict[str, Any]) -> DatabaseConfig | None:
        """Load and validate the database configuration section when present.

        Args:
            app_config: Pre-loaded application configuration dictionary.

        Returns:
            DatabaseConfig | None: Database config when it is fully defined, otherwise ``None``.

        Raises:
            ValueError: If a database section is present but malformed.
        """
        if "database" not in app_config:
            return None

        database_config = app_config.get("database")
        if database_config is None or database_config == {}:
            return None

        if not isinstance(database_config, dict):
            raise ValueError(
                "Config file is missing the '[database]' section. "
                "Please ensure that the section is present and valid."
            )

        required_fields = ["host", "port", "name"]
        missing_fields = [field for field in required_fields if field not in database_config]
        if missing_fields:
            raise ValueError(
                "Config file is missing required fields. "
                "Please ensure that 'host', 'port', and 'name' are present."
            )

        return DatabaseConfig(**database_config)
