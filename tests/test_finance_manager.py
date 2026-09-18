import pytest
from decimal import Decimal
from pathlib import Path

from unittest.mock import Mock, call, patch, mock_open
from finance_manager import FinanceManager
from domain.wallet import Wallet
from google_sheets_data.row_dto import GoogleSheetsRowDTO

MAGIC_TOML_CONTENT = b"""[google_sheets]
spreadsheet_id = "exemplary_spreadsheets_id"
credentials_path = "road/to/hogwarts"
worksheets = ["Sickles"]

[database]
host = "localhogwarts"
port = 3407
name = "pages_in_hp"
"""


def test_load_config():
    """Test loading successful configuration from a valid config.toml file."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=MAGIC_TOML_CONTENT)),
    ):
        fm = FinanceManager(config_path=Path("hogwarts_configuration.toml"))

        assert fm._config.google_config is not None
        assert fm._config.google_config.spreadsheet_id == "exemplary_spreadsheets_id"
        assert fm._config.google_config.credentials_path == "road/to/hogwarts"
        assert fm._config.google_config.worksheets == ["Sickles"]


def test_missing_file():
    """Test running FinanceManager with missing credentials file."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            FinanceManager(config_path=Path("fake/road/to/hogwarts"))

@pytest.mark.parametrize("credentials_file_exists", [True, False])
def test_missing_credentials_file(credentials_file_exists):
    """Test running FinanceManager load_sheets_data with missing credentials file"""
    with (patch('pathlib.Path.exists', return_value=True), 
          patch('pathlib.Path.open', mock_open(read_data=MAGIC_TOML_CONTENT))):
        fm = FinanceManager(config_path =  Path("hogwarts_configuration.toml")) 

    with (patch('pathlib.Path.exists', return_value=credentials_file_exists),
          patch('finance_manager.GoogleSheetsHoldingParser') as holdling_mock):
        if not credentials_file_exists:
            with pytest.raises(FileNotFoundError):
                fm.load_sheets_data()
            holdling_mock.assert_not_called()
        else:
            fm.load_sheets_data()
            holdling_mock.assert_called_once()


def test_build_wallet():
    """Build portfolios and assets from parsed Google Sheets rows."""
    manager = object.__new__(FinanceManager)
    manager.wallet = Wallet()
    manager.load_sheets_data = Mock(return_value=[
        GoogleSheetsRowDTO("stock", "Retirement", "Acme", Decimal("2"), "USD", "ACME"),
        GoogleSheetsRowDTO("cash", "Retirement", "Savings", Decimal("100"), "PLN"),
        GoogleSheetsRowDTO("gold", "Emergency", "Gold", Decimal("1.5"), "PLN"),
    ])
    created_assets = [Mock(name="stock_asset"), Mock(name="cash_asset"), Mock(name="gold_asset")]

    with patch("finance_manager.AssetFactory.create", side_effect=created_assets) as create_asset:
        manager.build_wallet()

    assert [portfolio.name for portfolio in manager.wallet.get_portfolios()] == [
        "Retirement",
        "Emergency",
    ]
    assert manager.wallet.get_portfolios()[0].assets == created_assets[:2]
    assert manager.wallet.get_portfolios()[1].assets == created_assets[2:]
    assert create_asset.call_args_list == [
        call(asset_type="stock", name="Acme", currency="USD", quantity=Decimal("2"), ticker="ACME"),
        call(asset_type="cash", name="Savings", currency="PLN", quantity=Decimal("100")),
        call(asset_type="gold", name="Gold", currency="PLN", quantity=Decimal("1.5")),
    ]