from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from db.models import AssetSnapshotModel, Base, PortfolioSnapshotModel, WalletModel, WalletSnapshotModel
from db.repository import SnapshotRepository
from domain.assets.asset import Asset
from domain.wallet import Wallet


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as database_session:
            yield database_session
    finally:
        engine.dispose()


def make_wallet() -> Wallet:
    """Create a wallet with themed test data."""
    wallet = Wallet("Gringotts Wallet")
    wallet.add_portfolio("Harry's Vault")
    wallet.add_portfolio("Hermione's Vault")
    asset = Mock(spec=Asset)
    asset.asset_type = "Stock"
    asset.name = "Daily Prophet"
    asset.ticker = "DP"
    asset.quantity = Decimal("2.5")
    asset.currency = "Galleons"
    asset.unit_price_in_currency = Decimal("12.34567890")
    asset.total_value_pln = Decimal("30.86")
    wallet.add_asset_to_portfolio(
        "Harry's Vault",
        asset,
    )
    return wallet


def test_save_snapshot_persists_complete_wallet_graph(session: Session) -> None:
    """Test saving a wallet persists portfolios and assets as one snapshot."""
    snapshot_time = datetime(2026, 9, 9, 12, 30, tzinfo=timezone.utc)

    snapshot = SnapshotRepository(session).save_snapshot(make_wallet(), snapshot_time)

    assert snapshot.id is not None
    assert snapshot.wallet.name == "Gringotts Wallet"
    assert snapshot.timestamp.replace(tzinfo=timezone.utc) == snapshot_time
    assert [portfolio.name for portfolio in snapshot.portfolios] == ["Harry's Vault", "Hermione's Vault"]
    asset = snapshot.portfolios[0].assets[0]
    assert asset.asset_type == "Stock"
    assert asset.name == "Daily Prophet"
    assert asset.ticker == "DP"
    assert asset.quantity == Decimal("2.50000000")
    assert asset.currency == "Galleons"
    assert asset.unit_price_in_currency == Decimal("12.34567890")
    assert asset.total_value_pln == Decimal("30.86")


def test_save_snapshot_reuses_wallet_and_creates_new_snapshot(session: Session) -> None:
    """Test repeated runs reuse the wallet identity and create snapshots."""
    repository = SnapshotRepository(session)

    repository.save_snapshot(make_wallet())
    repository.save_snapshot(make_wallet())

    wallet = session.scalar(select(WalletModel).where(WalletModel.name == "Gringotts Wallet"))
    wallets = session.scalars(select(WalletModel)).all()
    snapshots = session.scalars(select(WalletSnapshotModel)).all()

    assert wallet is not None
    assert wallet.id == 1
    assert len(wallets) == 1
    assert len(snapshots) == 2


def test_save_snapshot_supports_empty_wallet(session: Session) -> None:
    """Test an empty wallet still creates a snapshot without portfolios."""
    snapshot = SnapshotRepository(session).save_snapshot(Wallet("Dumbledore's Empty Vault"))

    assert snapshot.wallet.name == "Dumbledore's Empty Vault"
    assert snapshot.portfolios == []


def test_save_snapshot_rejects_invalid_values(session: Session) -> None:
    """Test invalid wallet names and timestamps are rejected."""
    repository = SnapshotRepository(session)

    with pytest.raises(ValueError, match="Wallet name cannot be empty"):
        repository.save_snapshot(Wallet("   "))

    with pytest.raises(ValueError, match="timezone-aware"):
        repository.save_snapshot(Wallet("Main"), datetime(2026, 9, 9))


def test_snapshot_rows_have_expected_foreign_key_links(session: Session) -> None:
    """Test snapshot child rows reference their parent rows."""
    snapshot = SnapshotRepository(session).save_snapshot(make_wallet())

    portfolio = session.scalar(
        select(PortfolioSnapshotModel).where(PortfolioSnapshotModel.wallet_snapshot_id == snapshot.id)
    )
    asset = session.scalar(
        select(AssetSnapshotModel).where(AssetSnapshotModel.portfolio_snapshot_id == portfolio.id)
    )

    assert portfolio.wallet_snapshot_id == snapshot.id
    assert asset.portfolio_snapshot_id == portfolio.id
