
import json
import asyncio
import ssl

import websockets


class MexcFuturesSocketClient:

    def __init__(self):
        self.BASE_URL = 'wss://contract.mexc.com/ws'
        self.SERVER_PING_METHOD = 'ping'
        self.KLINE_METHOD = 'sub.kline'        

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
                print('exception from mexc_futures_socket_client.ping: ', ex)                  

            await asyncio.sleep(30)


    async def kline_subscribe(self, symbol: str, interval: str, callback):            

        data = {
            "method": self.KLINE_METHOD,
            "param":{
                "symbol": symbol,
                "interval": interval
            }         
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
                    print('exception from mexc_futures_socket_client.kline_subscribe: ', ex)                                  

        except Exception as ex_sub:
            print('exception from mexc_futures_socket_client.kline_subscribe: ', ex_sub) 
