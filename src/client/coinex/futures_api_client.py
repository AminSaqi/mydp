
import aiohttp
import pandas as pd


class CoinexFuturesApiClient:

    def __init__(self):
        self.BASE_URL = 'https://api.coinex.com/perpetual/v1'
        self.KLINES_ENDPOINT = self.BASE_URL + '/market/kline'


    async def get_klines(self, symbol: str, timeframe: str, count=500):    

        connector = aiohttp.TCPConnector(limit=None)
        async with aiohttp.ClientSession(connector=connector) as session:

            try:
                url = '{}?market={}&type={}&limit={}'.format(self.KLINES_ENDPOINT, symbol, timeframe, count)
                async with session.get(url) as resp:
                    r_json = await resp.json()                          
                    return r_json['data']                    

            except Exception as ex:
                print('exception from coinex_futures.get_klines: ', ex)
                return None