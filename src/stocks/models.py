from dataclasses import dataclass
from typing import Dict, List

from src.database.userstocks.models import UserStock
from src.stocks.polygon.models import StockPrices


@dataclass
class Portfolio:

    stocks: Dict[str, UserStock]
    prices: Dict[str, StockPrices]

    def get_stocks(self) -> List[str]:
        return self.stocks.keys()

    def get_latest_price(self, symbol: str) -> float:
        return self.prices[symbol].prices[-1].price

    def get_number_of_shares(self, symbol: str) -> float:
        return self.stocks[symbol].quantity

    def get_equity(self, symbol: str) -> float:
        price = self.get_latest_price(symbol)
        shares = self.get_number_of_shares(symbol)
        return price * shares

    def get_total_equity(self) -> float:
        equity = 0
        for stock in self.stocks.keys():
            equity += self.get_equity(stock)
        return equity