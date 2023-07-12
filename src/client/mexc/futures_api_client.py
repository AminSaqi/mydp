
import aiohttp
import pandas as pd


class MexcFuturesApiClient:

    def __init__(self):
        self.BASE_URL = 'https://contract.mexc.com'
        self.KLINES_ENDPOINT = self.BASE_URL + '/api/v1/contract/kline'


    async def get_klines(self, symbol: str, timeframe: str, count=500):    

        connector = aiohttp.TCPConnector(limit=None, verify_ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:

            try:
                url = '{}/{}?interval={}&limit={}'.format(self.KLINES_ENDPOINT, symbol, timeframe, count)
                async with session.get(url) as resp:
                    r_json = await resp.json()                                       
                    return r_json['data']                    

            except Exception as ex:
                print('exception from mexc_futures.get_klines: ', ex)
                return None