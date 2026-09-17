from abc import ABC, abstractmethod
from datetime import datetime, timezone
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import AssetSnapshotModel, PortfolioSnapshotModel, WalletModel, WalletSnapshotModel

from domain.wallet import Wallet

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SnapshotRepositoryInterface(ABC):
    """Abstract base class defining the repository contract for saving snapshot aggregates."""

    @abstractmethod
    def save_snapshot(self, wallet: Wallet, snapshot_time: datetime | None = None) -> WalletSnapshotModel:
        """Persists a complete time-series snapshot for a given wallet."""
        pass


class SnapshotRepository(SnapshotRepositoryInterface):
    """SQLAlchemy implementation of the SnapshotRepositoryInterface.
    
    Handles the conversion and persistence of domain portfolio data into time-series
    snapshot models for historical visualization in Grafana.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create_wallet(self, wallet_name: str) -> WalletModel:
        """Fetches an existing WalletModel by name or creates a new one if it does not exist.
        
        Args:
            wallet_name: The name of the wallet to fetch or create.

        Returns:
            The existing or newly created WalletModel instance.

        Raises:
            ValueError: If the wallet_name is empty or only whitespace.
        """
        if not wallet_name.strip():
            raise ValueError("Wallet name cannot be empty.")

        wallets = select(WalletModel).where(WalletModel.name == wallet_name)
        wallet = self.session.scalars(wallets).first()

        if not wallet:
            logger.info("Adding new wallet: %s", wallet_name)
            wallet = WalletModel(name=wallet_name)
            self.session.add(wallet)
            self.session.flush()  # Flush to populate wallet.id

        return wallet

    def save_snapshot(self, wallet: Wallet, snapshot_time: datetime | None = None) -> WalletSnapshotModel:
        """Saves a complete point-in-time snapshot of all sub-portfolios and their assets.

        Args:
            wallet: The Wallet domain object containing portfolios and assets to snapshot.
            snapshot_time: Optional timestamp for the snapshot. Defaults to current UTC time.

        Returns:
            The created WalletSnapshotModel entity.
        """
        if snapshot_time is None:
            snapshot_time = datetime.now(timezone.utc)
        elif snapshot_time.tzinfo is None:
            raise ValueError("snapshot_time must be timezone-aware.")

        wallet_model = self.get_or_create_wallet(wallet.name)
        wallet_snapshot = WalletSnapshotModel(wallet_id=wallet_model.id, timestamp=snapshot_time)

        for portfolio in wallet.portfolios:
            portfolio_snapshot = PortfolioSnapshotModel(name=portfolio.name)

            for asset in portfolio.assets:
                asset_snapshot = AssetSnapshotModel(
                    asset_type=asset.asset_type,
                    name=asset.name,
                    ticker=asset.ticker,
                    quantity=asset.quantity,
                    currency=asset.currency,
                    unit_price_in_currency=asset.unit_price_in_currency,
                    total_value_pln=asset.total_value_pln
                )
                portfolio_snapshot.assets.append(asset_snapshot)

            wallet_snapshot.portfolios.append(portfolio_snapshot)

        self.session.add(wallet_snapshot)
        self.session.commit()
        self.session.refresh(wallet_snapshot)

        return wallet_snapshot