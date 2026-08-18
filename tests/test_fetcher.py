from unittest.mock import Mock, patch

from google_sheets_data.fetcher import READ_ONLY_SCOPES, GoogleSheetsFetcher


SPREADSHEET_ID = "exemplary_spreadsheets_id"
CREDENTIALS_PATH = "road/to/credentials.json"


def test_initialize_fetcher():
	"""Test initializing the fetcher with service account credentials."""
	credentials = Mock()
	client = Mock()
	spreadsheet = Mock()

	with (patch("google_sheets_data.fetcher.Credentials.from_service_account_file", return_value=credentials) as credentials_mock,
		  patch("google_sheets_data.fetcher.gspread.authorize", return_value=client) as authorize_mock):
		client.open_by_key.return_value = spreadsheet

		fetcher = GoogleSheetsFetcher(CREDENTIALS_PATH, SPREADSHEET_ID)

	credentials_mock.assert_called_once_with(CREDENTIALS_PATH, scopes=READ_ONLY_SCOPES)
	authorize_mock.assert_called_once_with(credentials)
	client.open_by_key.assert_called_once_with(SPREADSHEET_ID)
	assert fetcher._spreadsheet is spreadsheet


def test_fetch_worksheet():
	"""Test fetching all values from a worksheet."""
	fetcher = object.__new__(GoogleSheetsFetcher)
	spreadsheet = Mock()
	worksheet = Mock()
	worksheet.get_all_values.return_value = [["name", "value"], ["Savings", "100"]]
	spreadsheet.worksheet.return_value = worksheet
	fetcher._spreadsheet = spreadsheet

	result = fetcher.fetch_worksheet("Sickles")

	spreadsheet.worksheet.assert_called_once_with("Sickles")
	worksheet.get_all_values.assert_called_once_with()
	assert result == [["name", "value"], ["Savings", "100"]]


def test_fetch_worksheets():
	"""Test fetching all values from multiple worksheets."""
	fetcher = object.__new__(GoogleSheetsFetcher)
	fetcher.fetch_worksheet = Mock(side_effect=[[["Sickles"]], [["Galleons"]]])

	result = fetcher.fetch_worksheets(["Savings", "Investments"])

	fetcher.fetch_worksheet.assert_any_call("Savings")
	fetcher.fetch_worksheet.assert_any_call("Investments")
	assert result == {"Savings": [["Sickles"]], "Investments": [["Galleons"]]}
