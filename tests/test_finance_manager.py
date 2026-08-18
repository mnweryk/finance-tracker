import pytest
from pathlib import Path

from unittest.mock import patch, Mock, mock_open
from finance_manager import FinanceManager

MAGIC_TOML_CONTENT = b"""[google_sheets]
spreadsheet_id = "exemplary_spreadsheets_id"
credentials_path = "road/to/hogwarts"
worksheets = ["Sickles"]
"""

def test_load_config():
    """ Test loading successful configuration from a valid config.toml file."""
    with (patch('pathlib.Path.exists', return_value=True), 
          patch('pathlib.Path.open', mock_open(read_data=MAGIC_TOML_CONTENT))):
        fm = FinanceManager(config_path =  Path("hogwarts_configuration.toml"))

        assert fm._config.spreadsheet_id == "exemplary_spreadsheets_id"
        assert fm._config.credentials_path == "road/to/hogwarts"
        assert fm._config.worksheets == ["Sickles"]

def test_load_empty_config():
    """Test loading empty config"""
    with (patch('pathlib.Path.exists', return_value=True), 
          patch('pathlib.Path.open', mock_open(read_data=b""))):
        with pytest.raises(ValueError):
            FinanceManager(config_path =  Path("hogwarts_configuration.toml"))

@pytest.mark.parametrize("missing_field", [
    "credentials_path",
    "spreadsheet_id",
    "worksheets",
])
def test_load_config_missing_field(missing_field):
    """Test loading configuration with missing required fields in the config.toml file."""
    toml_content = "[google_sheets]"
    for field in ["credentials_path","spreadsheet_id", "worksheets"]:
        if field != missing_field:
            toml_content += f'\n{field} = "expecto_patronum"'

    with (patch('pathlib.Path.exists', return_value=True), 
        patch('pathlib.Path.open', mock_open(read_data=toml_content.encode()))):
        with pytest.raises(ValueError):
            FinanceManager(config_path=Path("road/to/hogwarts"))

def test_missing_file():
    """Test running FinanceManager with missing credentials file"""
    with patch('pathlib.Path.open', return_value=False):
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