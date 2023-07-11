
import pandas as pd

from src.base.enums import Exchange
from src.base.interfaces import ExchangeProxy
from src.base.types import DataEventFuncType
from src.proxy import ( 
    BinanceSpotProxy, 

    CoinexSpotProxy,
    CoinexFuturesProxy,

    KucoinSpotProxy, 

    MexcSpotProxy 
)
from src.base.results import ServiceResult
import src.base.errors as error


class DataManager():

    def __init__(self, config: 'list[dict]', push_data_event_func: DataEventFuncType):

        self.__push_data_event_func = push_data_event_func

        self.__exchanges: 'dict[str, ExchangeProxy]' = {}

        for exchange_config in config:
            exchange_name = exchange_config['exchange']            
            exchange = Exchange(exchange_name)
            symbols_config = exchange_config['symbols']
            exchange_proxy = self.__get_exchange_proxy(exchange, symbols_config)

            self.__exchanges[exchange.value] = exchange_proxy                    


    def __get_exchange_proxy(self, exchange: Exchange, symbols_config: 'list[dict]'):

        if exchange is Exchange.BinanceSpot:
            return BinanceSpotProxy(Exchange.BinanceSpot.value, symbols_config, self.__push_data_event_func)        
        elif exchange is Exchange.BinanceFutures:
            raise NotImplementedError()
        
        elif exchange is Exchange.BingxSpot:
            return NotImplementedError()
        elif exchange is Exchange.BingxFutures:
            raise NotImplementedError()
        
        elif exchange is Exchange.CoinexSpot:
            return CoinexSpotProxy(Exchange.CoinexSpot.value, symbols_config, self.__push_data_event_func)        
        elif exchange is Exchange.CoinexFutures:
            return CoinexFuturesProxy(Exchange.CoinexFutures.value, symbols_config, self.__push_data_event_func)
        
        elif exchange is Exchange.KucoinSpot:
            return KucoinSpotProxy(Exchange.KucoinSpot.value, symbols_config, self.__push_data_event_func)        
        elif exchange is Exchange.KucoinFutures:
            raise NotImplementedError()
        
        elif exchange is Exchange.MexcSpot:
            return MexcSpotProxy(Exchange.MexcSpot.value, symbols_config, self.__push_data_event_func)        
        elif exchange is Exchange.MexcFutures:
            raise NotImplementedError()


    def __get_exchange(self, exchange_name: str):

        if exchange_name in self.__exchanges:
            return self.__exchanges[exchange_name]
        else:
            return None


    def get_candles(self, exchange_name: str, symbol_name: str, timeframe: str, count: int):
        
        exchange = self.__get_exchange(exchange_name)
        if exchange is None:
            return ServiceResult[pd.DataFrame](success=False, message=error.INVALID_EXCHANGE)

        return exchange.get_candles(symbol_name, timeframe, count)

        
        



