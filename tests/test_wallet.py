from decimal import Decimal
from unittest.mock import Mock
import logging

import pytest

from domain.wallet import Wallet
from domain.portfolio import Portfolio
from domain.assets.asset import Asset


@pytest.fixture
def sample_wallet() -> Wallet:
    """Create a wallet for testing."""
    return Wallet()


@pytest.fixture
def mock_asset() -> Mock:
    """Create a mock asset with basic properties."""
    asset = Mock(spec=Asset)
    asset.asset_type = "Stock"
    asset.total_value_pln = Decimal("1000.00")
    return asset


def test_wallet_initialization():
    """Test wallet is initialized with empty portfolios list."""
    wallet = Wallet()

    assert wallet.portfolios == []
    assert isinstance(wallet.portfolios, list)


def test_add_portfolio_single(sample_wallet):
    """Test adding a single portfolio to the wallet."""
    sample_wallet.add_portfolio("Gringotts Vault")

    assert len(sample_wallet.portfolios) == 1
    assert sample_wallet.portfolios[0].name == "Gringotts Vault"


def test_add_portfolio_multiple(sample_wallet):
    """Test adding multiple portfolios to the wallet."""
    sample_wallet.add_portfolio("Harry's Vault")
    sample_wallet.add_portfolio("Hermione's Vault")
    sample_wallet.add_portfolio("Ron's Vault")

    assert len(sample_wallet.portfolios) == 3
    assert sample_wallet.portfolios[0].name == "Harry's Vault"
    assert sample_wallet.portfolios[1].name == "Hermione's Vault"
    assert sample_wallet.portfolios[2].name == "Ron's Vault"


def test_get_portfolios(sample_wallet):
    """Test get_portfolios returns the wallet's portfolio list."""
    sample_wallet.add_portfolio("Gringotts Vault")
    portfolios = sample_wallet.get_portfolios()

    assert len(portfolios) == 1
    assert portfolios[0].name == "Gringotts Vault"



def test_add_asset_to_portfolio_success(sample_wallet, mock_asset):
    """Test adding an asset to an existing portfolio."""
    sample_wallet.add_portfolio("Gringotts Vault")
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", mock_asset)

    assert len(sample_wallet.portfolios[0].assets) == 1
    assert sample_wallet.portfolios[0].assets[0] == mock_asset


def test_add_asset_to_portfolio_not_found():
    """Test adding an asset to a non-existent portfolio raises ValueError."""
    wallet = Wallet()
    asset = Mock(spec=Asset)

    with pytest.raises(ValueError, match="Portfolio with name 'Nonexistent Vault' not found"):
        wallet.add_asset_to_portfolio("Nonexistent Vault", asset)


def test_add_asset_to_portfolio_multiple_assets(sample_wallet):
    """Test adding multiple assets to the same portfolio."""
    sample_wallet.add_portfolio("Gringotts Vault")

    asset1 = Mock(spec=Asset)
    asset1.total_value_pln = Decimal("500.00")

    asset2 = Mock(spec=Asset)
    asset2.total_value_pln = Decimal("1500.00")

    sample_wallet.add_asset_to_portfolio("Gringotts Vault", asset1)
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", asset2)

    assert len(sample_wallet.portfolios[0].assets) == 2


def test_get_total_value_pln_empty_wallet(sample_wallet):
    """Test total value for an empty wallet is zero."""
    total = sample_wallet.get_total_value_pln()

    assert total == Decimal(0)


def test_get_total_value_pln_single_portfolio_single_asset(sample_wallet, mock_asset):
    """Test total value with one portfolio and one asset."""
    sample_wallet.add_portfolio("Gringotts Vault")
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", mock_asset)

    total = sample_wallet.get_total_value_pln()

    assert total == Decimal("1000.00")


def test_get_total_value_pln_multiple_portfolios(sample_wallet):
    """Test total value sums all portfolios correctly."""
    sample_wallet.add_portfolio("Harry's Vault")
    sample_wallet.add_portfolio("Hermione's Vault")

    asset1 = Mock(spec=Asset)
    asset1.total_value_pln = Decimal("1000.00")

    asset2 = Mock(spec=Asset)
    asset2.total_value_pln = Decimal("2500.00")

    asset3 = Mock(spec=Asset)
    asset3.total_value_pln = Decimal("500.00")

    sample_wallet.add_asset_to_portfolio("Harry's Vault", asset1)
    sample_wallet.add_asset_to_portfolio("Harry's Vault", asset2)
    sample_wallet.add_asset_to_portfolio("Hermione's Vault", asset3)

    total = sample_wallet.get_total_value_pln()

    assert total == Decimal("4000.00")


@pytest.mark.parametrize("values", [
    [Decimal("100.00"), Decimal("200.00"), Decimal("300.00")],
    [Decimal("1000.50"), Decimal("2000.75"), Decimal("500.25")],
    [Decimal("9999.99")],
])
def test_get_total_value_pln_various_amounts(sample_wallet, values):
    """Test total value calculation with various amounts across portfolios."""
    expected_total = sum(values)
    for i, value in enumerate(values):
        sample_wallet.add_portfolio(f"Vault {i}")
        asset = Mock(spec=Asset)
        asset.total_value_pln = value
        sample_wallet.add_asset_to_portfolio(f"Vault {i}", asset)

    assert sample_wallet.get_total_value_pln() == expected_total


def test_print_wallet_portfolios_empty(sample_wallet):
    """Test wallet summary for an empty wallet."""
    summary = sample_wallet.print_wallet_portfolios()

    assert "Wallet Summary:" in summary
    assert "Total Wallet Value: 0.00 PLN" in summary


def test_print_wallet_portfolios_single_portfolio(sample_wallet, mock_asset):
    """Test wallet summary with one portfolio and asset."""
    sample_wallet.add_portfolio("Gringotts Vault")
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", mock_asset)

    summary = sample_wallet.print_wallet_portfolios()

    assert "Wallet Summary:" in summary
    assert "Gringotts Vault" in summary
    assert "Total Wallet Value: 1000.00 PLN" in summary


def test_print_wallet_portfolios_multiple_portfolios(sample_wallet):
    """Test wallet summary with multiple portfolios."""
    sample_wallet.add_portfolio("Harry's Vault")
    sample_wallet.add_portfolio("Hermione's Vault")

    asset1 = Mock(spec=Asset)
    asset1.asset_type = "Stock"
    asset1.total_value_pln = Decimal("2000.00")

    asset2 = Mock(spec=Asset)
    asset2.asset_type = "Crypto"
    asset2.total_value_pln = Decimal("3000.00")

    sample_wallet.add_asset_to_portfolio("Harry's Vault", asset1)
    sample_wallet.add_asset_to_portfolio("Hermione's Vault", asset2)

    summary = sample_wallet.print_wallet_portfolios()

    assert "Wallet Summary:" in summary
    assert "Harry's Vault" in summary
    assert "Hermione's Vault" in summary
    assert "Total Wallet Value: 5000.00 PLN" in summary


def test_get_wallet_by_asset_type_empty(sample_wallet):
    """Test asset type grouping for an empty wallet."""
    assets_by_type = sample_wallet.get_wallet_by_asset_type()

    assert assets_by_type == {}


def test_get_wallet_by_asset_type_single_type(sample_wallet, mock_asset):
    """Test asset type grouping with assets of one type."""
    sample_wallet.add_portfolio("Gringotts Vault")
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", mock_asset)

    assets_by_type = sample_wallet.get_wallet_by_asset_type()

    assert "Stock" in assets_by_type
    assert len(assets_by_type["Stock"]) == 1
    assert assets_by_type["Stock"][0] == mock_asset


def test_get_wallet_by_asset_type_multiple_types(sample_wallet):
    """Test asset type grouping with multiple asset types."""
    sample_wallet.add_portfolio("Gringotts Vault")

    stock_asset = Mock(spec=Asset)
    stock_asset.asset_type = "Stock"
    stock_asset.total_value_pln = Decimal("1000.00")

    crypto_asset = Mock(spec=Asset)
    crypto_asset.asset_type = "Crypto"
    crypto_asset.total_value_pln = Decimal("500.00")

    bond_asset = Mock(spec=Asset)
    bond_asset.asset_type = "Bond"
    bond_asset.total_value_pln = Decimal("2000.00")

    sample_wallet.add_asset_to_portfolio("Gringotts Vault", stock_asset)
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", crypto_asset)
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", bond_asset)

    assets_by_type = sample_wallet.get_wallet_by_asset_type()

    assert "Stock" in assets_by_type
    assert "Crypto" in assets_by_type
    assert "Bond" in assets_by_type
    assert len(assets_by_type["Stock"]) == 1
    assert len(assets_by_type["Crypto"]) == 1
    assert len(assets_by_type["Bond"]) == 1


def test_get_wallet_by_asset_type_multiple_portfolios(sample_wallet):
    """Test asset type grouping across multiple portfolios."""
    sample_wallet.add_portfolio("Harry's Vault")
    sample_wallet.add_portfolio("Hermione's Vault")

    asset1 = Mock(spec=Asset)
    asset1.asset_type = "Stock"
    asset1.total_value_pln = Decimal("1000.00")

    asset2 = Mock(spec=Asset)
    asset2.asset_type = "Stock"
    asset2.total_value_pln = Decimal("500.00")

    asset3 = Mock(spec=Asset)
    asset3.asset_type = "Crypto"
    asset3.total_value_pln = Decimal("2000.00")

    sample_wallet.add_asset_to_portfolio("Harry's Vault", asset1)
    sample_wallet.add_asset_to_portfolio("Harry's Vault", asset2)
    sample_wallet.add_asset_to_portfolio("Hermione's Vault", asset3)

    assets_by_type = sample_wallet.get_wallet_by_asset_type()

    assert len(assets_by_type["Stock"]) == 2
    assert len(assets_by_type["Crypto"]) == 1


def test_get_wallet_summary_by_asset_type_empty(sample_wallet):
    """Test summary by asset type for an empty wallet."""
    summary = sample_wallet.get_wallet_summary_by_asset_type()

    assert "Wallet Summary by Asset Type:" in summary
    assert "total: 0.00 PLN" in summary


def test_get_wallet_summary_by_asset_type_single_asset(sample_wallet, mock_asset):
    """Test summary by asset type with one asset."""
    sample_wallet.add_portfolio("Gringotts Vault")
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", mock_asset)

    summary = sample_wallet.get_wallet_summary_by_asset_type()

    assert "Wallet Summary by Asset Type:" in summary
    assert "total: 1000.00 PLN" in summary
    assert "Stock:" in summary


def test_get_wallet_summary_by_asset_type_multiple_assets(sample_wallet):
    """Test summary by asset type with multiple asset types."""
    sample_wallet.add_portfolio("Gringotts Vault")

    stock_asset = Mock(spec=Asset)
    stock_asset.asset_type = "Stock"
    stock_asset.total_value_pln = Decimal("1000.00")

    crypto_asset = Mock(spec=Asset)
    crypto_asset.asset_type = "Crypto"
    crypto_asset.total_value_pln = Decimal("500.00")

    sample_wallet.add_asset_to_portfolio("Gringotts Vault", stock_asset)
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", crypto_asset)

    summary = sample_wallet.get_wallet_summary_by_asset_type()

    assert "Wallet Summary by Asset Type:" in summary
    assert "total: 1500.00 PLN" in summary
    assert "Stock:" in summary
    assert "Crypto:" in summary


def test_str_calls_get_wallet_summary_by_asset_type(sample_wallet, mock_asset):
    """Test __str__ method returns wallet summary by asset type."""
    sample_wallet.add_portfolio("Gringotts Vault")
    sample_wallet.add_asset_to_portfolio("Gringotts Vault", mock_asset)

    wallet_str = str(sample_wallet)
    summary = sample_wallet.get_wallet_summary_by_asset_type()

    assert wallet_str == summary


@pytest.mark.parametrize("portfolio_names", [
    ["Vault 1"],
    ["Harry's Vault", "Hermione's Vault"],
    ["Gringotts Vault", "Hogsmeade Vault", "Diagon Alley Vault"],
])
def test_add_multiple_portfolios_parametrized(sample_wallet, portfolio_names):
    """Test adding multiple portfolios with parametrized names."""
    for name in portfolio_names:
        sample_wallet.add_portfolio(name)

    assert len(sample_wallet.portfolios) == len(portfolio_names)
    for i, name in enumerate(portfolio_names):
        assert sample_wallet.portfolios[i].name == name
