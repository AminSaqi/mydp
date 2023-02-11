
from itertools import repeat

import pandas as pd
from binance.spot import Spot
from binance.websocket.spot.websocket_client import SpotWebsocketClient
from binance.error import ClientError

class BinanceSpotProxy():

    def __init__(self, symbols_config: 'list[dict]'):
         
        self.__data: 'dict[tuple[str, str], pd.DataFrame]' = {}

        self.__symbols_config: 'dict[str, list]' = { conf['symbol']: conf['timeframes'] for conf in symbols_config }

        self.__api_client: Spot = Spot()
        self.__socket_client = SpotWebsocketClient()
        self.__socket_client.start()       

        self.__prepare_historical_data()
        self.__connect_to_data_streams() 

#%% Historical data

    def __prepare_historical_data(self):
        
        symbols = self.__symbols_config.keys()
        for symbol in symbols:
            timeframes = self.__symbols_config['timeframes']
            for timeframe in timeframes:
                df = self.__fetch_kline(symbol, timeframe)
                self.__data[(symbol, timeframe)] = df

        
    def __fetch_kline(self, symbol, timeframe):
        
        klines = self.__api_client.klines(symbol=symbol, interval=timeframe)
        df = pd.DataFrame(klines)
        df.drop(df.columns[[6, 7, 8, 9, 10, 11]], axis=1, inplace=True)  # Remove unnecessary columns
        df = self.__parse_dataframe(df)

        return df


    def __parse_dataframe(self, df_klines):   
        
        df = df_klines.copy()
        df.columns = ['open_timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        df['open_datetime'] = pd.to_datetime(df['open_timestamp'], unit='ms')
        df = df.set_index('open_datetime')        
        
        return df

#%% Socket data.

    def __connect_to_data_streams(self):

        streams = []
        stream_postfix = '@kline_{}'

        symbols = self.__symbols_config.keys()     
        for symbol in symbols:
            tfs = self.__symbols_config[symbol]
            symbol_streams = [symbol.lower() + st for st in [stream_postfix.format(tf) for tf in tfs]]        
            streams.append(symbol_streams)

        self.__socket_client.live_subscribe(stream=streams, id=1, callback=self.__handle_socket_message)


    def __handle_socket_message(self, msg):    
                
        if ('stream' in msg) and ('data' in msg):
            self.__handle_data_event(msg['data'])

        elif 'e' in msg:            

            if msg['e'] == 'kline': 
                self.__handle_data_event(msg)

            elif msg['e'] == 'error':
                #TODO: log error
                raise msg     


    def __handle_data_event(self, msg):

        """https://binance-docs.github.io/apidocs/spot/en/#kline-candlestick-streams""" 

        symbol = msg['s']        
        kline = msg['k']
        timeframe = kline['i']
        
        candle = {
            'open_timestamp': kline['T'],
            'open_datetime': pd.to_datetime(kline['T'], unit='ms'),
            'open': kline['o'],
            'high': kline['h'],
            'low': kline['l'],
            'close': kline['c'],
            'volume': kline['v']
        }

        row = pd.DataFrame.from_records(data=[candle], index='open_datetime')

        if (symbol, timeframe) in self.__data:
            df = self.__data[symbol]            
            df_new = row.combine_first(df).tail(500)
            self.__data[symbol] = df_new
        else:
            self.__data[symbol] = row
      
           


