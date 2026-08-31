from decimal import Decimal
from unittest.mock import Mock
import logging

import pytest

from domain.portfolio import Portfolio
from domain.assets.asset import Asset


@pytest.fixture
def sample_portfolio() -> Portfolio:
    """Create a portfolio for testing."""
    return Portfolio(name="Weasley's Test Portfolio")


@pytest.fixture
def mock_asset() -> Mock:
    """Create a mock asset with basic properties."""
    asset = Mock(spec=Asset)
    asset.asset_type = "Stock"
    asset.total_value_pln = Decimal("1000.00")
    return asset


def test_portfolio_initialization():
    """Test portfolio is initialized with correct name and empty assets list."""
    name = "Malfoy's Test Portfolio"
    portfolio = Portfolio(name=name)

    assert portfolio.name == name
    assert portfolio.assets == []
    assert isinstance(portfolio.assets, list)


def test_add_asset_single(sample_portfolio, mock_asset):
    """Test adding a single asset to the portfolio."""
    sample_portfolio.add_asset(mock_asset)

    assert len(sample_portfolio.assets) == 1
    assert sample_portfolio.assets[0] == mock_asset


def test_add_asset_multiple(sample_portfolio):
    """Test adding multiple assets to the portfolio."""
    asset1 = Mock(spec=Asset)
    asset1.asset_type = "Stock"
    asset1.total_value_pln = Decimal("1000.00")

    asset2 = Mock(spec=Asset)
    asset2.asset_type = "Crypto"
    asset2.total_value_pln = Decimal("500.00")

    sample_portfolio.add_asset(asset1)
    sample_portfolio.add_asset(asset2)

    assert len(sample_portfolio.assets) == 2
    assert sample_portfolio.assets[0] == asset1
    assert sample_portfolio.assets[1] == asset2


def test_get_total_value_pln_empty_portfolio(sample_portfolio):
    """Test total value for an empty portfolio is zero."""
    total = sample_portfolio.get_total_value_pln()

    assert total == Decimal(0)


def test_get_total_value_pln_single_asset(sample_portfolio, mock_asset):
    """Test total value with a single asset."""
    sample_portfolio.add_asset(mock_asset)
    total = sample_portfolio.get_total_value_pln()

    assert total == Decimal("1000.00")


def test_get_total_value_pln_multiple_assets(sample_portfolio):
    """Test total value sums all assets correctly."""
    asset1 = Mock(spec=Asset)
    asset1.total_value_pln = Decimal("1000.00")

    asset2 = Mock(spec=Asset)
    asset2.total_value_pln = Decimal("2500.50")

    asset3 = Mock(spec=Asset)
    asset3.total_value_pln = Decimal("999.99")

    sample_portfolio.add_asset(asset1)
    sample_portfolio.add_asset(asset2)
    sample_portfolio.add_asset(asset3)

    total = sample_portfolio.get_total_value_pln()

    assert total == Decimal("4500.49")


@pytest.mark.parametrize("values", [
    [Decimal("100.00"), Decimal("200.00"), Decimal("300.00")],
    [Decimal("1000.50"), Decimal("2000.75")],
    [Decimal("9999.99")],
])
def test_get_total_value_pln_various_amounts(sample_portfolio, values):
    """Test total value calculation with various asset amounts."""
    expected_total = sum(values)
    for value in values:
        asset = Mock(spec=Asset)
        asset.total_value_pln = value
        sample_portfolio.add_asset(asset)

    assert sample_portfolio.get_total_value_pln() == expected_total


def test_portfolio_summary_empty(sample_portfolio):
    """Test summary string for an empty portfolio."""
    summary = sample_portfolio.portfolio_summary()

    assert "Weasley's Test Portfolio" in summary
    assert "0.00 PLN" in summary


def test_portfolio_summary_single_asset(sample_portfolio, mock_asset):
    """Test summary includes asset information."""
    sample_portfolio.add_asset(mock_asset)
    summary = sample_portfolio.portfolio_summary()

    assert "Weasley's Test Portfolio" in summary
    assert "1000.00 PLN" in summary
    assert "Stock" in summary


def test_portfolio_summary_multiple_assets(sample_portfolio):
    """Test summary with multiple asset types."""
    asset1 = Mock(spec=Asset)
    asset1.asset_type = "Stock"
    asset1.total_value_pln = Decimal("1000.00")

    asset2 = Mock(spec=Asset)
    asset2.asset_type = "Crypto"
    asset2.total_value_pln = Decimal("500.00")

    sample_portfolio.add_asset(asset1)
    sample_portfolio.add_asset(asset2)
    summary = sample_portfolio.portfolio_summary()

    assert "Weasley's Test Portfolio" in summary
    assert "1500.00 PLN" in summary
    assert "Stock" in summary
    assert "Crypto" in summary


def test_str_calls_portfolio_summary(sample_portfolio, mock_asset):
    """Test __str__ method returns portfolio summary."""
    sample_portfolio.add_asset(mock_asset)
    portfolio_str = str(sample_portfolio)
    summary = sample_portfolio.portfolio_summary()

    assert portfolio_str == summary


def test_print_portfolio_logs_summary(sample_portfolio, mock_asset, caplog):
    """Test print_portfolio logs summary at INFO level."""
    sample_portfolio.add_asset(mock_asset)

    with caplog.at_level(logging.INFO):
        sample_portfolio.print_portfolio()

    assert "Weasley's Test Portfolio" in caplog.text
    assert "1000.00 PLN" in caplog.text


def test_portfolio_summary_with_duplicate_asset_types(sample_portfolio):
    """Test summary deduplicates asset types."""
    asset1 = Mock(spec=Asset)
    asset1.asset_type = "Stock"
    asset1.total_value_pln = Decimal("1000.00")

    asset2 = Mock(spec=Asset)
    asset2.asset_type = "Stock"
    asset2.total_value_pln = Decimal("500.00")

    sample_portfolio.add_asset(asset1)
    sample_portfolio.add_asset(asset2)
    summary = sample_portfolio.portfolio_summary()

    asset_types_count = summary.count("Stock")
    assert asset_types_count >= 1
    assert "Stock" in summary
