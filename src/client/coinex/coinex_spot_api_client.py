
import aiohttp
import pandas as pd


class CoinexSpotApiClient:

    def __init__(self):
        self.BASE_URL = 'https://api.coinex.com/v1'
        self.KLINES_ENDPOINT = self.BASE_URL + '/market/kline'


    async def get_klines(self, symbol: str, timeframe: str, count=500):    

        connector = aiohttp.TCPConnector(limit=None)
        async with aiohttp.ClientSession(connector=connector) as session:

            try:
                url = '{}?market={}&type={}&limit={}'.format(self.KLINES_ENDPOINT, symbol, timeframe, count)
                async with session.get(url) as resp:
                
                    r_json = await resp.json()     

                    df = pd.DataFrame(data=r_json['data'])   
                    df.columns = ['open_timestamp', 'open', 'close', 'high', 'low', 'volume', 'quote_volume']                    

                    df['open_datetime'] = pd.to_datetime(df['open_timestamp'], unit='s')
                    df = df.set_index('open_datetime')  

                    df['open'] = df['open'].astype('float')
                    df['high'] = df['high'].astype('float')
                    df['low'] = df['low'].astype('float')
                    df['close'] = df['close'].astype('float')
                    df['volume'] = df['volume'].astype('float')
                    df['quote_volume'] = df['quote_volume'].astype('float')

                    return df                    

            except Exception as ex:
                print('exception from coinex_spot.get_klines: ', ex)
                return None