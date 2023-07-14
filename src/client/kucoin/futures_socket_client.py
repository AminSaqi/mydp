
import aiohttp
import asyncio
import time


class KucoinFuturesSocketClient:

    def __init__(self):
        self.BASE_URL = 'https://api-futures.kucoin.com'
        self.KLINES_ENDPOINT = self.BASE_URL + '/api/v1/kline/query'


    async def kline_subscribe(self, symbol: str, timeframe: str, granularity: int, callback):    
        
        connector = aiohttp.TCPConnector(limit=None, verify_ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:

            while True:
                try:
                    ts_from = (time.time_ns() // 1_000_000) - 86_400_000                
                    url = '{}?symbol={}&granularity={}&from={}'.format(self.KLINES_ENDPOINT, symbol, granularity, ts_from)

                    async with session.get(url) as resp:
                        r_json = await resp.json()                                                              
                        callback(symbol, timeframe, r_json)

                except Exception as ex:
                    print('exception from bingx_futures.get_klines: ', ex)
                    return None
                
                await asyncio.sleep(2)