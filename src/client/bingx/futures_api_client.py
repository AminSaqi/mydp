
import aiohttp
import time


class BingxFuturesApiClient:

    def __init__(self):
        self.BASE_URL = 'https://open-api.bingx.com'
        self.KLINES_ENDPOINT = self.BASE_URL + '/openApi/swap/v2/quote/klines'


    async def get_klines(self, symbol: str, timeframe: str, count=500):    
        
        connector = aiohttp.TCPConnector(limit=None, verify_ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:

            try:
                ts_now_plus_one_day = (time.time_ns() // 1_000_000) + 86_400_000                
                url = '{}?symbol={}&interval={}&endTime={}&limit={}'.format(self.KLINES_ENDPOINT, symbol, timeframe, ts_now_plus_one_day, count)

                async with session.get(url) as resp:
                    r_json = await resp.json()                                                       
                    return r_json['data']                    

            except Exception as ex:
                print('exception from bingx_futures.get_klines: ', ex)
                return None