
import json
import asyncio
import ssl

import websockets


class MexcSpotSocketClient:

    def __init__(self):
        self.BASE_URL = 'wss://wbs.mexc.com/ws'
        self.SERVER_PING_METHOD = 'PING'
        self.SUBSCRIPTION_METHOD = 'SUBSCRIPTION'        

    async def init(self):

        ssl_context = ssl.SSLContext()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.__websocket = await websockets.connect(self.BASE_URL,
                                                    ping_interval=None,
                                                    ssl=ssl_context)


    async def ping(self):
        
        data = {
            "method": self.SERVER_PING_METHOD
        }

        payload = json.dumps(data)

        while True:
            try:
                await self.__websocket.send(payload)                                                          

            except Exception as ex:
                print('exception from mexc_spot_socket_client.ping: ', ex)                  

            await asyncio.sleep(30)


    async def kline_subscribe(self, symbol: str, interval: str, callback):            

        param = 'spot@public.kline.v3.api@{}@{}'.format(symbol, interval)

        data = {
            "method": self.SUBSCRIPTION_METHOD,
            "params":[
                param
            ]                    
        }

        payload = json.dumps(data)
        
        try:
            await self.__websocket.send(payload)
            response = await self.__websocket.recv()           
        
            while True:
                try:                    
                    response = await self.__websocket.recv()                     
                    dict_r = json.loads(response)              
                    callback(dict_r)                

                except Exception as ex:
                    print('exception from mexc_spot_socket_client.kline_subscribe: ', ex)                                  

        except Exception as ex_sub:
            print('exception from mexc_spot_socket_client.kline_subscribe: ', ex_sub) 