
import json
import asyncio

import websockets


class CoinexSpotSocketClient:

    def __init__(self):
        self.BASE_URL = 'wss://socket.coinex.com/'
        self.SERVER_PING_METHOD = 'server.ping'
        self.KLINES_QUERY_METHOD = 'kline.query'        

    async def init(self):
        self.__websocket = await websockets.connect(self.BASE_URL, compression='deflate')


    async def ping(id=1):
        pass


    async def kline_query(self, symbol: str, fromTimestamp: int, intervalSeconds: int, callback, id):            

        data = {
            "method":"kline.query",
            "params":[
                symbol,
                fromTimestamp,
                fromTimestamp + 1_000_000_000,
                intervalSeconds
            ],
            "id": id
        }

        paylod = json.dumps(data)

        while True:
            try:
                await self.__websocket.send(paylod)
                response = await self.__websocket.recv()
                callback(response)                

            except Exception as ex:
                print('exception from coinex_spot.get_klines: ', ex)  

            asyncio.sleep(2)