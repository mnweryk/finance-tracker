from unittest.mock import MagicMock, patch

import pytest
from gspread.exceptions import SpreadsheetNotFound, WorksheetNotFound

from fetchers.google_sheets import READ_ONLY_SCOPES, GoogleSheetsFetcher


@pytest.fixture
def mock_gspread():
    """Mocks Credentials and gspread.authorize, returning client and spreadsheet objects."""
    with patch("fetchers.google_sheets.Credentials.from_service_account_file") as mock_creds, \
         patch("fetchers.google_sheets.gspread.authorize") as mock_authorize:
        
        mock_credentials = MagicMock()
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()

        mock_creds.return_value = mock_credentials
        mock_authorize.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet

        yield {
            "creds": mock_creds,
            "credentials_obj": mock_credentials,
            "authorize": mock_authorize,
            "client": mock_client,
            "spreadsheet": mock_spreadsheet,
        }


def test_init_authenticates_and_opens_spreadsheet(mock_gspread):
    """Checks if initialization loads credentials with the correct scope and opens the spreadsheet by ID."""
    creds_path = "path/to/creds.json"
    sheet_id = "test_spreadsheet_123"

    fetcher = GoogleSheetsFetcher(credentials_path=creds_path, spreadsheet_id=sheet_id)

    mock_gspread["creds"].assert_called_once_with(creds_path, scopes=READ_ONLY_SCOPES)

    mock_gspread["authorize"].assert_called_once_with(mock_gspread["credentials_obj"])

    mock_gspread["client"].open_by_key.assert_called_once_with(sheet_id)

    assert fetcher._spreadsheet == mock_gspread["spreadsheet"]


def test_init_raises_when_spreadsheet_not_found(mock_gspread):
    """Checks if initialization raises SpreadsheetNotFound when the spreadsheet is not found."""
    mock_gspread["client"].open_by_key.side_effect = SpreadsheetNotFound("Spreadsheet not found")
    with pytest.raises(SpreadsheetNotFound):
        GoogleSheetsFetcher(credentials_path="path/to/creds.json", spreadsheet_id="test_spreadsheet_123")


def test_fetch_worksheet_success(mock_gspread):
    """Checks if fetch_worksheet returns a matrix of rows fetched from a worksheet."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_values.return_value = [
        ["Data", "Kategoria", "Kwota"],
        ["2026-01-01", "Jedzenie", "150.00"],
    ]
    
    mock_gspread["spreadsheet"].worksheet.return_value = mock_worksheet

    fetcher = GoogleSheetsFetcher(credentials_path="path/to/creds.json", spreadsheet_id="test_spreadsheet_123")
    rows = fetcher.fetch_worksheet("Stan")

    mock_gspread["spreadsheet"].worksheet.assert_called_once_with("Stan")
    mock_worksheet.get_all_values.assert_called_once()
    assert rows == [
        ["Data", "Kategoria", "Kwota"],
        ["2026-01-01", "Jedzenie", "150.00"],
    ]


def test_fetch_worksheet_not_found_raises_error(mock_gspread):
    """Checks if fetching a non-existent worksheet raises WorksheetNotFound."""
    mock_gspread["spreadsheet"].worksheet.side_effect = WorksheetNotFound("Worksheet not found")

    fetcher = GoogleSheetsFetcher(credentials_path="path/to/creds.json", spreadsheet_id="test_spreadsheet_123")

    with pytest.raises(WorksheetNotFound):
        fetcher.fetch_worksheet("Non-existent")

def test_fetch_worksheets_multiple(mock_gspread):
    """Checks if fetch_worksheets fetches all requested sheets and maps them by sheet name."""
    worksheet_stan = MagicMock()
    worksheet_stan.get_all_values.return_value = [["Stan_H1"], ["Stan_V1"]]

    worksheet_akcje = MagicMock()
    worksheet_akcje.get_all_values.return_value = [["Akcje_H1"], ["Akcje_V1"]]

    def mock_worksheet_lookup(name: str):
        if name == "Stan":
            return worksheet_stan
        if name == "Akcje":
            return worksheet_akcje
        raise WorksheetNotFound(name)

    mock_gspread["spreadsheet"].worksheet.side_effect = mock_worksheet_lookup

    fetcher = GoogleSheetsFetcher(credentials_path="path/to/creds.json", spreadsheet_id="test_spreadsheet_123")
    result = fetcher.fetch_worksheets(["Stan", "Akcje"])

    assert result == {
        "Stan": [["Stan_H1"], ["Stan_V1"]],
        "Akcje": [["Akcje_H1"], ["Akcje_V1"]],
    }


def test_fetch_worksheets_empty_list(mock_gspread):
    """Checks if fetching an empty list of worksheets returns an empty dictionary immediately."""
    fetcher = GoogleSheetsFetcher(credentials_path="path/to/creds.json", spreadsheet_id="test_spreadsheet_123")
    
    result = fetcher.fetch_worksheets([])

    assert result == {}

    mock_gspread["spreadsheet"].worksheet.assert_not_called()