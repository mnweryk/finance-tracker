from decimal import Decimal

from .asset import Asset
from .bond import Bond
from .cash import Cash
from .crypto import Crypto
from .gold import Gold
from .stock import Stock


class AssetFactory:
    """Create concrete asset objects from worksheet asset type names."""

    _ASSET_TYPES: dict[str, type[Asset]] = {
        "cash": Cash,
        "stock": Stock,
        "bond": Bond,
        "crypto": Crypto,
        "gold": Gold,
    }

    @classmethod
    def create(cls, asset_type: str, name: str, currency: str, quantity: Decimal, ticker: str | None = None) -> Asset:
        """Create an asset matching a case-insensitive asset type.

        Args:
            asset_type: Asset type key, such as ``cash`` or ``stock``.
            name: Human-readable asset name.
            currency: Currency in which the asset is valued.
            quantity: Number of units held.
            ticker: Optional market ticker required by some asset types.

        Returns:
            A concrete ``Asset`` instance for the requested type.

        Raises:
            ValueError: If ``asset_type`` is not supported.
        """
        try:
            asset_class = cls._ASSET_TYPES[asset_type.lower()]
        except KeyError:
            raise ValueError(f"Unknown asset type: {asset_type}")

        kwargs = {
            "name": name,
            "currency": currency,
            "quantity": quantity,
        }
        if ticker is not None:
            kwargs["ticker"] = ticker
        return asset_class(**kwargs)