
from enum import Enum


class Exchange(Enum):
    BinanceSpot = 'binance_spot'
    BinanceFutures = 'binance_futures'
    KucoinSpot = 'kucoin_spot'
    KucoinFutures = 'kucoin_futures'
    CoinexSpot = 'coinex_spot'
    CoinexFutures = 'coinex_futures'

