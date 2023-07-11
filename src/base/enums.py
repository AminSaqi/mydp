
from enum import Enum


class Exchange(Enum):
    BinanceSpot = 'binance_spot'
    BinanceFutures = 'binance_futures'
    BingxSpot = 'bingx_spot'
    BingxFutures = 'bingx_futures'
    CoinexSpot = 'coinex_spot'
    CoinexFutures = 'coinex_futures'
    KucoinSpot = 'kucoin_spot'
    KucoinFutures = 'kucoin_futures'
    MexcSpot = 'mexc_spot'
    MexcFutures = 'mexc_futures'

