from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class WalletModel(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    snapshots: Mapped[list["WalletSnapshotModel"]] = relationship(back_populates="wallet", cascade="all, delete-orphan")


class WalletSnapshotModel(Base):
    """Represents a single execution run of the tracker script (a point-in-time snapshot)."""
    __tablename__ = "wallet_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id"), nullable=False)

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    wallet: Mapped["WalletModel"] = relationship(back_populates="snapshots",)

    portfolios: Mapped[list["PortfolioSnapshotModel"]] = relationship(back_populates="wallet_snapshot", cascade="all, delete-orphan")


class PortfolioSnapshotModel(Base):
    """Represents a sub-portfolio state within a specific wallet snapshot."""
    __tablename__ = "portfolio_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    wallet_snapshot_id: Mapped[int] = mapped_column(ForeignKey("wallet_snapshots.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    wallet_snapshot: Mapped["WalletSnapshotModel"] = relationship(back_populates="portfolios")

    assets: Mapped[list["AssetSnapshotModel"]] = relationship(back_populates="portfolio_snapshot", cascade="all, delete-orphan")


class AssetSnapshotModel(Base):
    """Represents the state and valuation of a single asset within a specific portfolio snapshot.
    
    This table stores time-series historical data queried directly by Grafana.
    """
    __tablename__ = "asset_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    portfolio_snapshot_id: Mapped[int] = mapped_column(ForeignKey("portfolio_snapshots.id"), nullable=False)

    asset_type: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ticker: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Quantity of asset units held at the time of the snapshot
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)

    unit_price_in_currency: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    total_value_pln: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    portfolio_snapshot: Mapped["PortfolioSnapshotModel"] = relationship(back_populates="assets")