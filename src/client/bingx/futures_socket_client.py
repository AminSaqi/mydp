
import json
import asyncio
import ssl

import websockets


class BingxFuturesSocketClient:

    def __init__(self):
        self.BASE_URL = 'wss://open-api-swap.bingx.com/swap-market'                                

    async def init(self):

        ssl_context = ssl.SSLContext()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.__websocket = await websockets.connect(self.BASE_URL,
                                                    compression='deflate',
                                                    ping_interval=None,                                                                                                        
                                                    ssl=ssl_context)    


    async def kline_subscribe(self, id: str, symbol: str, interval: str, callback):            

        pong_data = {
            "dataType": "Pong"
        }

        sub_data = {
            "id": id,
            "regType": "sub",
            "dataType": "{}@kline_{}".format(symbol, interval)                  
        }

        pong_payload = json.dumps(pong_data)
        sub_payload = json.dumps(sub_data)
        
        try:
            await self.__websocket.send(sub_payload)
            response = await self.__websocket.recv()  
        
            while True:
                try:                    
                    response = await self.__websocket.recv()  
                    dict_r = json.loads(response)     
                    print(dict_r)
                    #TODO: check for ping and send pong.
                    #          
                    callback(dict_r)                

                except Exception as ex:
                    print('exception from bingx_futures_socket_client.kline_subscribe: ', ex)                                  

        except Exception as ex_sub:
            print('exception from bingx_futures_socket_client.kline_subscribe: ', ex_sub) 
