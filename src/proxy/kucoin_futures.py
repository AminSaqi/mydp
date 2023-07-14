
import asyncio

import nest_asyncio
nest_asyncio.apply()

import pandas as pd
from kucoin_futures.client import Market
from kucoin_futures.client import WsToken
from kucoin_futures.ws_client import KucoinFuturesWsClient

from src.client.kucoin import KucoinFuturesSocketClient
from src.base.types import DataEventFuncType
from src.base.interfaces import ExchangeProxy
from src.base.results import ServiceResult
import src.base.errors as error

class KucoinFuturesProxy(ExchangeProxy):

    def __init__(self, exchange_name: str, symbols_config: 'list[dict]', push_data_event_func: DataEventFuncType):
         
        self.__exchange_name = exchange_name

        self.__data: 'dict[tuple[str, str], pd.DataFrame]' = {}

        self.__symbols_config: 'dict[str, tuple(list, list)]' = \
            { conf['symbol']: (conf['timeframes'], conf['aliases']) for conf in symbols_config }

        self.__push_data_event_func = push_data_event_func

        self.__api_client: Market = Market(url="https://api-futures.kucoin.com")
        self.__socket_client: KucoinFuturesSocketClient = KucoinFuturesSocketClient()            

        self.__prepare_historical_data()
       
        loop = asyncio.get_event_loop()
        loop.create_task(self.__connect_to_data_streams())               


#%% Historical data setup.


    def __prepare_historical_data(self):
        
        symbols = self.__symbols_config.keys()
        for symbol in symbols:            
            timeframes = self.__symbols_config[symbol][0]
            for timeframe in timeframes:
                df = self.__fetch_kline(symbol, timeframe)
                self.__data[(symbol, timeframe)] = df # df[::-1]

        
    def __fetch_kline(self, symbol, timeframe):
        
        granularity = self.__get_granularity_from_timeframe(timeframe)
        klines = self.__api_client.get_kline_data(symbol=symbol, granularity=granularity)
        df = pd.DataFrame(klines)        
        df = self.__parse_dataframe(df)

        return df


    def __get_granularity_from_timeframe(self, timeframe):

        timeframe_to_granularity = {
            "1min": 1,
            "5min": 5,
            "15min": 15,
            "30min": 30,
            "1hour": 60,
            "2hour": 120,
            "4hour": 240,
            "6hour": 360,
            "8hour": 480,
            "12hour": 720,
            "1day": 1440,
            "1week": 10080
        }

        return timeframe_to_granularity[timeframe]

    def __parse_dataframe(self, df_klines):   
        
        df = df_klines.copy()
        df.columns = ['open_timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        df['open_datetime'] = pd.to_datetime(df['open_timestamp'], unit='ms')
        df = df.set_index('open_datetime')   

        df = df[['open_timestamp', 'open', 'high', 'low', 'close', 'volume']]     
        
        return df


#%% Socket setup.


    async def __connect_to_data_streams(self):          
            
        streams = []
        
        symbols = self.__symbols_config.keys()     
        for symbol in symbols:

            tupple_tfs_aliases = self.__symbols_config[symbol]

            for timeframe in tupple_tfs_aliases[0]:

                stream = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "granularity": self.__get_granularity_from_timeframe(timeframe),                    
                    "callback": self.__handle_socket_message
                }
                           
                streams.append(stream)
    
        await self.__subscribe_to_topics(streams) 


    def __handle_socket_message(self, symbol, timeframe, msg):                    
                
        if ('data' in msg):            
            self.__handle_data_event(symbol, timeframe, msg)

        else:
            #TODO: log error
            print(msg)


    def __handle_data_event(self, symbol, timeframe, msg): 

        data = msg['data']        
        kline = data[-1]       
        
        candle = {
            'open_timestamp': kline[0],
            'open_datetime': pd.to_datetime(kline[0], unit='ms'),
            'open': kline[1],
            'high': kline[2],
            'low': kline[3],
            'close': kline[4],
            'volume': kline[5]
        }

        row = pd.DataFrame.from_records(data=[candle], index='open_datetime')

        if (symbol, timeframe) in self.__data:
            df = self.__data[(symbol, timeframe)]            
            df_new = row.combine_first(df).tail(500)
            self.__data[(symbol, timeframe)] = df_new
        else:
            self.__data[(symbol, timeframe)] = row

        candle['open_datetime'] = str(candle['open_datetime'])

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        background_tasks = list()
        task = loop.create_task(self.__push_data_event_func(self.__exchange_name, symbol, timeframe, candle))   
        background_tasks.append(task)    
        task.add_done_callback(background_tasks.remove)
        loop.run_until_complete(asyncio.wait(background_tasks))  
       

    async def __subscribe_to_topics(self, list_topics: 'list[str]'):
        
        loop = asyncio.get_event_loop()        
        for topic in list_topics:           
            loop.create_task(self.__socket_client.kline_subscribe(**topic))           
                
            


#%% Data methods.


    def __get_symbol_config(self, symbol_name):        

        if symbol_name in self.__symbols_config:
            return symbol_name, self.__symbols_config[symbol_name]
        
        else:
            for key in self.__symbols_config:
                symbol_config = self.__symbols_config[key]               
                if symbol_name in symbol_config[1]:
                    return key, symbol_config
        
        return None, None


    def get_candles(self, symbol_name: str, timeframe: str, count: int) -> ServiceResult[pd.DataFrame]:

        result = ServiceResult[pd.DataFrame]()

        config_key, symbol_config = self.__get_symbol_config(symbol_name)     

        if symbol_config is None:
            result.success = False
            result.message = error.INVALID_SYMBOL
            return result

        if timeframe not in symbol_config[0]:
            result.success = False
            result.message = error.INVALID_TIMEFRAME
            return result

        key = (config_key, timeframe)
        df = self.__data[key].tail(count).copy()
        df = df.reset_index()
        df = df[['open_timestamp', 'open_datetime', 'open', 'high', 'low', 'close', 'volume']]  

        result.success = True
        result.result = df

        return result
        
        
