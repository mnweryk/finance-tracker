import logging
import requests
import yfinance as yf
from decimal import Decimal
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

STOCK_TICKER_MAPPINGS: dict[str, str] = {
    "WSE": "WA",
    "AMS": "AS",
    "LON": "L",
    "BIT": "DE",
    "NYSE": ""
}

DELISTED_STOCKS: list[str] = ["WSE:IRL"]

class MarketDataProvider:
    """Provide market prices, currency rates, and PLN conversion support."""

    @staticmethod
    def get_stock_price(ticker: str) -> Decimal:
        """Fetch the current stock price for an exchange-qualified ticker.

        Args:
            ticker: Ticker in ``EXCHANGE:SYMBOL`` format.

        Returns:
            Decimal: Current price in the stock's trading currency.

        Raises:
            ValueError: If the exchange is unsupported or no price is available.
        """
        if ticker in DELISTED_STOCKS:
            logger.debug(f"Ticker {ticker} is delisted. Returning 0 as price.")
            return Decimal(0)
        exchange, stock_ticker = ticker.split(":")
        if exchange not in STOCK_TICKER_MAPPINGS:
            raise ValueError(f"Exchange {exchange} not supported.")

        mapped_ticker = f"{stock_ticker}.{STOCK_TICKER_MAPPINGS[exchange]}" if STOCK_TICKER_MAPPINGS[exchange] else stock_ticker

        data = yf.Ticker(mapped_ticker)
        last_price = data.fast_info.get('lastPrice')
        if not last_price:
            raise ValueError(f"Could not fetch exchange rate for {ticker} to PLN.")
        
        return Decimal(last_price)

    @staticmethod
    def get_currency_pln_rate(currency: str) -> Decimal:
        """Fetch the current exchange rate of a currency to PLN using yfinance.

        Args:
            currency: ISO currency code. ``PLN`` returns a rate of one.

        Returns:
            Decimal: Current exchange rate to PLN.

        Raises:
            ValueError: If no exchange rate is available.
        """
        if currency == "PLN":
            return Decimal(1)

        ticker = f"{currency}PLN=X"
        data = yf.Ticker(ticker)
        last_price = data.fast_info.get('lastPrice')
        if not last_price:
            raise ValueError(f"Could not fetch exchange rate for {currency} to PLN.")

        return Decimal(last_price)

    @staticmethod
    def convert_to_pln(func: Callable[..., Decimal]) -> Callable[..., Decimal]:
        """Decorate a value calculation with conversion from ``self.currency`` to PLN.

        Args:
            func: Function returning a value in the asset's currency.

        Returns:
            Callable[..., Decimal]: Wrapped function returning the value in PLN.
        """
        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Decimal:
            value = func(self, *args, **kwargs)
            rate = MarketDataProvider.get_currency_pln_rate(self.currency)
            return value * rate

        return wrapper

    @staticmethod
    def get_crypto_price(ticker: str) -> Decimal:
        """Fetch the current cryptocurrency price in USD using yfinance.

        Args:
            ticker: Cryptocurrency symbol without the ``-USD`` suffix.

        Returns:
            Decimal: Current cryptocurrency price in USD.

        Raises:
            ValueError: If no price is available.
        """
        data = yf.Ticker(f"{ticker}-USD")
        last_price = data.fast_info.get('lastPrice')
        if not last_price:
            raise ValueError(f"Could not fetch price for cryptocurrency {ticker}.")

        return Decimal(last_price)

    @staticmethod
    def get_gold_price_pln() -> Decimal:
        """Fetch the NBP gold price and convert it to the provider's unit.

        Returns:
            Decimal: NBP gold price multiplied by ``31.1034768``.

        Raises:
            requests.HTTPError: If the NBP request fails.
            ValueError: If the response does not contain a gold price.
        """
        response = requests.get("http://api.nbp.pl/api/cenyzlota?format=json")
        response.raise_for_status()

        data = response.json()
        price = data[0].get("cena")
        if price is None:
            raise ValueError("Could not fetch gold price from NBP API.")
        grams_per_ounce = Decimal("31.1034768")
        return Decimal(price)*grams_per_ounce
