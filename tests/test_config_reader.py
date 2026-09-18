import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from config_reader import ConfigReader

MAGIC_TOML_CONTENT = b"""[google_sheets]
spreadsheet_id = "exemplary_spreadsheets_id"
credentials_path = "road/to/hogwarts"
worksheets = ["Sickles"]

[database]
host = "localhogwarts"
port = 3407
name = "pages_in_hp"
"""


def test_load_google_sheets_config():
    """Test parsing the Google Sheets config section into the reader state."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=MAGIC_TOML_CONTENT)),
    ):
        reader = ConfigReader()

    assert reader.google_config is not None
    assert reader.google_config.spreadsheet_id == "exemplary_spreadsheets_id"
    assert reader.google_config.credentials_path == "road/to/hogwarts"
    assert reader.google_config.worksheets == ["Sickles"]

def test_load_database_config():
    """Test parsing the database config section into the reader state."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=MAGIC_TOML_CONTENT)),
    ):
        reader = ConfigReader()

    assert reader.db_config is not None
    assert reader.db_config.host == "localhogwarts"
    assert reader.db_config.port == 3407
    assert reader.db_config.name == "pages_in_hp"


@pytest.mark.parametrize("database_section", [None, "[database]"])
def test_load_config_missing_database_section(database_section):
    """Test that a missing or empty database section raises an error."""
    toml_content = """[google_sheets]
spreadsheet_id = "exemplary_spreadsheets_id"
credentials_path = "road/to/hogwarts"
worksheets = ["Sickles"]
"""
    if database_section == "[database]":
        toml_content += "\n[database]\n"

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=toml_content.encode())),
    ):
        with pytest.raises(ValueError):
            ConfigReader()


def test_skip_database_config_allows_missing_database_section():
    """Test that database config can be skipped when database saving is disabled."""
    toml_content = b"""[google_sheets]
spreadsheet_id = "exemplary_spreadsheets_id"
credentials_path = "road/to/hogwarts"
worksheets = ["Sickles"]
"""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=toml_content)),
    ):
        reader = ConfigReader(require_database=False)

    assert reader.db_config is None


def test_load_empty_config():
    """Test loading empty config."""
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=b"")),
    ):
        with pytest.raises(ValueError):
            ConfigReader()


@pytest.mark.parametrize("missing_field", [
    "credentials_path",
    "spreadsheet_id",
    "worksheets",
])
def test_load_config_missing_field(missing_field):
    """Test loading configuration with missing required fields in the config.toml file."""
    toml_content = "[google_sheets]"
    for field in ["credentials_path", "spreadsheet_id", "worksheets"]:
        if field != missing_field:
            toml_content += f'\n{field} = "expecto_patronum"'

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.open", mock_open(read_data=toml_content.encode())),
    ):
        with pytest.raises(ValueError):
            ConfigReader()


def test_missing_file():
    """Test running config reader with a missing config file."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            ConfigReader()
