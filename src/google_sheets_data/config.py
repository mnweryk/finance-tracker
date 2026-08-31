from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleSheetsConfig:
    """Configuration required to read holdings from Google Sheets.

    Attributes:
        credentials_path: Path to the service account credentials file.
        spreadsheet_id: ID of the Google Spreadsheet to open.
        worksheets: Names of worksheet tabs containing holdings data.
    """

    credentials_path: str
    spreadsheet_id: str
    worksheets: list[str]