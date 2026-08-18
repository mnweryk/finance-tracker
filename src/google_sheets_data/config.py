from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleSheetsConfig:
    credentials_path: str
    spreadsheet_id: str
    worksheets: list[str]