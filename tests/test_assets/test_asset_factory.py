from domain.assets.asset_factory import AssetFactory
from domain.assets.bond import Bond
from domain.assets.cash import Cash
from domain.assets.crypto import Crypto
from domain.assets.gold import Gold
from domain.assets.stock import Stock



from decimal import Decimal

import pytest

@pytest.mark.parametrize("bond_str", ["Bond", "bond", "BOND"])
def test_asset_factory_upper_lower_case(bond_str):
    asset = AssetFactory.create(
        asset_type=bond_str,
        name="Ministry of Magic Bond",
        currency="KNU",
        quantity=Decimal("5"),
        ticker="MM"
    )
    assert isinstance(asset, Bond)
    assert asset.name == "Ministry of Magic Bond"
    assert asset.currency == "KNU"
    assert asset.quantity == Decimal("5")
    assert asset.ticker == "MM"

@pytest.mark.parametrize(
    ["name", "expected_type", "ticker"], [
        ("cash", Cash, None),
        ("stock", Stock, "STOCK"),
        ("bond", Bond, "BOND"),
        ("crypto", Crypto, "CRYPTO"),
        ("gold", Gold, "GOLD")
    ])
def test_proper_object_creation(name, expected_type, ticker):
    kwargs = {
        "asset_type": name,
        "name": "Wizardy Asset",
        "currency": "KNU",
        "quantity": Decimal("1"),
    }
    if ticker is not None:
        kwargs["ticker"] = ticker

    asset = AssetFactory.create(**kwargs)
    assert isinstance(asset, expected_type)
    assert asset.name == "Wizardy Asset"
    assert asset.currency == "KNU" if name != "gold" else "PLN"
    assert asset.quantity == Decimal("1")
    if ticker is not None:
        assert asset.ticker == ticker

def test_invalid_asset_type():
    with pytest.raises(ValueError) as exc_info:
        AssetFactory.create(
            asset_type="muggle_asset",
            name="Muggle Asset",
            currency="PLN",
            quantity=Decimal("1")
        )
    assert "Unknown asset type: muggle_asset" in str(exc_info.value)