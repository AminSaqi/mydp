
import json
import asyncio
import ssl
import gzip
import io

import websockets


class BingxFuturesSocketClient:

    def __init__(self):
        self.BASE_URL = 'wss://open-api-swap.bingx.com/swap-market'  

        ssl_context = ssl.SSLContext()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.__ssl_context = ssl_context                                 


    async def kline_subscribe(self, id: str, symbol: str, interval: str, callback):                    

        async for websocket in websockets.connect(self.BASE_URL,
                                                    compression=None,
                                                    ping_interval=None,                                                                                                        
                                                    ssl=self.__ssl_context):
            sub_data = {
                "id": id,
                "reqType": "sub",
                "dataType": "{}@kline_{}".format(symbol, interval)                  
            }
            
            sub_payload = json.dumps(sub_data)
            
            while True:

                try:
                    await websocket.send(sub_payload)
                    response = await websocket.recv() 
                    await self.__handle_response(websocket, response, callback)
                
                    while True:
                        try:                    
                            response = await websocket.recv()                                            
                            await self.__handle_response(websocket, response, callback)

                        except Exception as ex:
                            print('exception from bingx_futures_socket_client.kline_subscribe: ', ex)   
                            break                               

                except websockets.ConnectionClosed:
                    print('Connection closed. Reconnecting {}@{} ...'.format(symbol, interval))                    
                
                except Exception as ex_sub:
                    print('exception from bingx_futures_socket_client.kline_subscribe: ', ex_sub) 

                await asyncio.sleep(5)


    async def __handle_response(self, websocket, response, callback):

        msg = self.__decode_message(response)       
        if msg == "Ping":
            await websocket.send("Pong")                        
        else:                                           
            callback(msg) 

    def __decode_message(self, response):

        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(response), mode='rb')
        decompressed_data = compressed_data.read()
        utf8_data = decompressed_data.decode('utf-8')  

        return utf8_data
