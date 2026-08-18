from typing import Any

import gspread
from google.oauth2.service_account import Credentials

READ_ONLY_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleSheetsFetcher:
    """Read-only fetcher for Google Spreadsheet worksheets."""

    def __init__(self, credentials_path: str, spreadsheet_id: str) -> None:
        """Initialize the fetcher with service account credentials and a spreadsheet ID.

        Args:
            credentials_path: Path to the Google service account JSON credentials file.
            spreadsheet_id: Google Spreadsheet ID to open.
        """
        credentials = Credentials.from_service_account_file(credentials_path, scopes=READ_ONLY_SCOPES)
        client = gspread.authorize(credentials)
        self._spreadsheet = client.open_by_key(spreadsheet_id)

    def fetch_worksheet(self, worksheet_name: str) -> list[list[Any]]:
        """Fetch all cell values from a single worksheet.

        Args:
            worksheet_name: Name of the worksheet tab to read.

        Returns:
            Raw worksheet rows, including the header row when present.
        """
        worksheet = self._spreadsheet.worksheet(worksheet_name)
        return worksheet.get_all_values()

    def fetch_worksheets(self, worksheet_names: list[str]) -> dict[str, list[list[Any]]]:
        """Fetch all cell values from multiple worksheets.

        Args:
            worksheet_names: Worksheet tab names to read.

        Returns:
            Mapping of worksheet name to raw worksheet rows.
        """
        return {worksheet_name: self.fetch_worksheet(worksheet_name) for worksheet_name in worksheet_names}
