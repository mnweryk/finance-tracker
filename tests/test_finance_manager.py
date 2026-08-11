from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from unittest.mock import mock_open

from fetchers.google_sheets import GoogleSheetsFetcher
from finance_manager import FinanceManager


@pytest.fixture
def mock_fetcher() -> MagicMock:
    """Creates a mock GoogleSheetsFetcher."""
    fetcher = MagicMock(spec=GoogleSheetsFetcher)
    fetcher.fetch_worksheets.return_value = {
        "Stan": [["Header1", "Header2"], ["Val1", "Val2"]],
        "Akcje": [["Ticker", "Amount"], ["AAPL", "10"]],
    }
    return fetcher


@pytest.fixture
def sample_config_file(tmp_path: Path) -> Path:
    """Creates a temporary valid config.toml file for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.toml"
    
    config_content = """
    [google_sheets]
    credentials_path = ".secrets/google_credentials.json"
    spreadsheet_id = "dummy_spreadsheet_id"
    worksheets = ["Stan", "Akcje"]
    """
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


def test_init_with_custom_fetcher(mock_fetcher: MagicMock, sample_config_file: Path) -> None:
    """Verify that FinanceManager uses injected fetcher and loads worksheet names from config."""
    manager = FinanceManager(fetcher=mock_fetcher, config_path=sample_config_file)
    
    assert manager._google_sheets_fetcher == mock_fetcher
    assert manager._worksheet_names == ["Stan", "Akcje"]


def test_load_sheets_data_forwards_to_fetcher(mock_fetcher: MagicMock, sample_config_file: Path) -> None:
    """Verify load_sheets_data delegates directly to GoogleSheetsFetcher.fetch_worksheets."""
    manager = FinanceManager(fetcher=mock_fetcher, config_path=sample_config_file)
    data = manager.load_sheets_data()

    mock_fetcher.fetch_worksheets.assert_called_once_with(["Stan", "Akcje"])
    assert "Stan" in data
    assert "Akcje" in data
    assert data["Stan"][0] == ["Header1", "Header2"]


def test_missing_config_file_raises_error(tmp_path: Path) -> None:
    """Verify FileNotFoundError is raised when config file does not exist."""
    non_existent_config = tmp_path / "missing_config.toml"
    
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        FinanceManager(config_path=non_existent_config)


@patch("finance_manager.Path.exists")
@patch(
    "finance_manager.Path.open",
    new_callable=mock_open,
    read_data=b'[google_sheets]\ncredentials_path=".secrets/fake.json"\nspreadsheet_id="dummy"\nworksheets=["Stan"]'
)
def test_missing_credentials_file_raises_error(mock_file, mock_exists):
    """Verify FileNotFoundError is raised when credentials JSON is missing (pure mock)."""
    mock_exists.side_effect = [True, False]

    with pytest.raises(FileNotFoundError, match="Google credentials file not found"):
        FinanceManager(config_path=Path("dummy_config.toml"))