
import json
import asyncio

import websockets


class CoinexFuturesSocketClient:

    def __init__(self):
        self.BASE_URL = 'wss://perpetual.coinex.com/'
        self.SERVER_PING_METHOD = 'server.ping'
        self.KLINES_QUERY_METHOD = 'kline.query'        

    async def init(self):
        self.__websocket = await websockets.connect(self.BASE_URL, 
                                                    compression='deflate',
                                                    ping_interval=None)


    async def ping(self):
        
        data = {
            "method": self.SERVER_PING_METHOD,
            "params": [],
            "id": 1
        }

        payload = json.dumps(data)

        while True:
            try:
                await self.__websocket.send(payload)
                # response = await self.__websocket.recv()  
                # dict_r = json.loads(response)
                # print(dict_r)                                              

            except Exception as ex:
                print('exception from coinex_futures_socket_client.ping: ', ex)                  

            await asyncio.sleep(60)


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

        payload = json.dumps(data)
        
        while True:
            try:
                await self.__websocket.send(payload)
                response = await self.__websocket.recv()  
                dict_r = json.loads(response)              
                callback(dict_r)                

            except Exception as ex:
                print('exception from coinex_futures_socket_client.get_klines: ', ex)                  

            await asyncio.sleep(2)