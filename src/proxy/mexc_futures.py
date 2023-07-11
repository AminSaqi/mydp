
import asyncio
import time

import nest_asyncio
nest_asyncio.apply()

import pandas as pd

from src.client.mexc.futures_api_client import MexcFuturesApiClient
from src.client.mexc.futures_socket_client import MexcFuturesSocketClient
from src.base.types import DataEventFuncType
from src.base.interfaces import ExchangeProxy
from src.base.results import ServiceResult
import src.base.errors as error

class MexcFuturesProxy(ExchangeProxy):

    def __init__(self, exchange_name: str, symbols_config: 'list[dict]', push_data_event_func: DataEventFuncType):
         
        self.__exchange_name = exchange_name

        self.__data: 'dict[tuple[str, str], pd.DataFrame]' = {}

        self.__symbols_config: 'dict[str, tuple(list, list)]' = \
            { conf['symbol']: (conf['timeframes'], conf['aliases']) for conf in symbols_config }                      

        self.__push_data_event_func = push_data_event_func

        self.__api_client: MexcFuturesApiClient = MexcFuturesApiClient()
        self.__socket_client: MexcFuturesSocketClient = MexcFuturesSocketClient()                      
               
        loop = asyncio.get_event_loop()        
        loop.create_task(self.__prepare_historical_data())                 


#%% Historical data setup.


    async def __prepare_historical_data(self):
        
        symbols = self.__symbols_config.keys()
        for symbol in symbols:            
            timeframes = self.__symbols_config[symbol][0]
            for timeframe in timeframes:
                df = await self.__fetch_kline(symbol, timeframe)
                self.__data[(symbol, timeframe)] = df # df[::-1]
        
        await self.__connect_to_data_streams()                

        
    async def __fetch_kline(self, symbol, timeframe):
        
        klines = await self.__api_client.get_klines(symbol=symbol, timeframe=timeframe)      
        df = pd.DataFrame(klines)
        df.drop(df.columns[[6, 7, 8, 9, 10]], axis=1, inplace=True)  # Remove unnecessary columns
        df = self.__parse_dataframe(df)

        return df


    def __parse_dataframe(self, df_klines):   
        
        df = df_klines.copy()
        df.columns = ['open_timestamp', 'open', 'close', 'high', 'low', 'volume']                    

        df['open_datetime'] = pd.to_datetime(df['open_timestamp'], unit='s')
        df = df.set_index('open_datetime')  

        df['open'] = df['open'].astype('float')
        df['high'] = df['high'].astype('float')
        df['low'] = df['low'].astype('float')
        df['close'] = df['close'].astype('float')
        df['volume'] = df['volume'].astype('float')        

        df = df[['open_timestamp', 'open', 'high', 'low', 'close', 'volume']]     
        
        return df


#%% Socket setup.


    async def __connect_to_data_streams(self):        
        
        await self.__initialize_socket_client()     

        streams = []
        
        symbols = self.__symbols_config.keys()     
        for symbol in symbols:

            tupple_tfs_aliases = self.__symbols_config[symbol]

            for timeframe in tupple_tfs_aliases[0]:

                stream = {
                    "symbol": symbol,                  
                    "interval": timeframe,
                    "callback": self.__handle_socket_message
                }
                           
                streams.append(stream)
    
        await self.__subscribe_to_topics(streams)       


    def __handle_socket_message(self, msg):    
        
        """https://mxcdevelop.github.io/apidocs/contract_v1_en/#public-channels"""
        
        if ('channel' in msg) and ('push.kline' in msg['channel']):                
            self.__handle_data_event(msg)

        else: 
            if ('channel' in msg) and (msg['channel'] == 'pong'):
                print('pong received.')

            else:              
                #TODO: log error
                print(msg)

    def __handle_data_event(self, msg): 
        
        kline = msg['data']
        symbol = kline['symbol']              
        timeframe = kline['interval']
                
        candle = {
            'open_timestamp': kline['t'],
            'open_datetime': pd.to_datetime(kline['t'], unit='s'),
            'open': kline['o'],
            'high': kline['h'],
            'low': kline['l'],
            'close': kline['c'],
            'volume': kline['a']
        }

        row = pd.DataFrame.from_records(data=[candle], index='open_datetime')

        if (symbol, timeframe) in self.__data:
            df = self.__data[(symbol, timeframe)]            
            df_new = row.combine_first(df).tail(500)
            self.__data[(symbol, timeframe)] = df_new
        else:
            self.__data[(symbol, timeframe)] = row

        candle['open_datetime'] = str(candle['open_datetime'])      

        loop = asyncio.get_event_loop()
        loop.create_task(self.__push_data_event_func(self.__exchange_name, symbol, timeframe, candle))


    async def __initialize_socket_client(self):

        await self.__socket_client.init()  

        loop = asyncio.get_event_loop()        
        loop.create_task(self.__socket_client.ping())   
          
    async def __subscribe_to_topics(self, list_topics: 'list[dict]'):
        
        for topic in list_topics:           
            await self.__socket_client.kline_subscribe(**topic)             
            

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
        
        
