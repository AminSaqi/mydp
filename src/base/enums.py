
from enum import Enum


class Exchange(Enum):
    BinanceSpot = 'binance_spot'
    BinanceFuturesUm = 'binance_futures_um'
    BinanceFuturesCm = 'binance_futures_cm'

    BingxSpot = 'bingx_spot'
    BingxFutures = 'bingx_futures'

    CoinexSpot = 'coinex_spot'
    CoinexFutures = 'coinex_futures'

    KucoinSpot = 'kucoin_spot'
    KucoinFutures = 'kucoin_futures'
    
    MexcSpot = 'mexc_spot'
    MexcFutures = 'mexc_futures'

