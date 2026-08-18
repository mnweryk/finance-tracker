import pytest
from decimal import Decimal
from unittest.mock import Mock, patch

from google_sheets_data.config import GoogleSheetsConfig
from google_sheets_data.holdings_parser import GoogleSheetsHoldingParser


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            [
                "Hermione", "", "Total Value", "10\xa0000,00 zł",
                "Ron", "", "Total Value", "15,00 zł",
                "Harry", "", "Total Value", "5\xa0300,00 zł",
            ],
            ["Hermione", "Ron", "Harry"],
        ),
        (
            ["Voldi", "total_value", "666"],
            ["Voldi"],
        ),
    ],
)
def test_portfolios(input, expected):
    assert GoogleSheetsHoldingParser.get_portfolios(input) == expected


def test_parse_row():
    """Test parsing asset data for each portfolio block."""
    parser = object.__new__(GoogleSheetsHoldingParser)
    row = [
        "Daily Prophet", "DP", " Galleons ", "2,5", "Gringotts", "GRI", "Knuts", "600%",
    ]
    portfolios = ["Harry's Wallet", "Hermione's"]
    column_mapping = {"Name": 0, "Ticker": 1, "Currency": 2, "Quantity": 3}

    dtos = parser.parse_row(row, portfolios, 4, column_mapping)

    assert len(dtos) == 2
    assert dtos[0].portfolio_name == "Harry's Wallet"
    assert dtos[0].name == "Daily Prophet"
    assert dtos[0].ticker == "DP"
    assert dtos[0].currency == "Galleons"
    assert dtos[0].quantity == Decimal("2.5")
    assert dtos[1].portfolio_name == "Hermione's"
    assert dtos[1].name == "Gringotts"
    assert dtos[1].ticker == "GRI"
    assert dtos[1].quantity == Decimal("6")


def test_create_dtos():
    """Test creating DTOs from the configured worksheet."""
    config = GoogleSheetsConfig(
        credentials_path="road/to/hogwarts/credentials.json",
        spreadsheet_id="hogwarts_spreadsheet_id",
        worksheets=["Hogwarts Holdings"],
    )
    fetcher = Mock()
    fetcher.fetch_worksheet.return_value = [
        ["Hogwarts Holdings"],
        ["Harry's Wallet", "100", "Hermione's", "250"],
        ["Name", "Ticker", "Currency", "Quantity", "Name", "Ticker", "Currency", "Quantity"],
        ["Daily Prophet", "DP", "Galleons", "2", "Gringotts", "GRI", "Knuts", "600"],
        ["Weasleys' Wizard Wheezes", "WWW", "Galleons", "1000"]
    ]

    with patch(
        "google_sheets_data.holdings_parser.GoogleSheetsFetcher",
        return_value=fetcher,
    ) as fetcher_class:
        parser = GoogleSheetsHoldingParser(config)

    assert len(parser.spreadsheet_dto) == 3

    assert parser.spreadsheet_dto[0].portfolio_name == "Harry's Wallet"
    assert parser.spreadsheet_dto[0].name == "Daily Prophet"

    assert parser.spreadsheet_dto[1].portfolio_name == "Hermione's"
    assert parser.spreadsheet_dto[1].name == "Gringotts"

    assert parser.spreadsheet_dto[2].portfolio_name == "Harry's Wallet"
    assert parser.spreadsheet_dto[2].name == "Weasleys' Wizard Wheezes"