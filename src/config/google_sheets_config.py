from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class GoogleSheetsConfig:
    credentials_path: Path
    spreadsheet_id: str
    worksheets: list[str]