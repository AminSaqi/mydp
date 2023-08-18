
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
                "regType": "sub",
                "dataType": "{}@kline_{}".format(symbol, interval)                  
            }

            pong_payload = "Pong"
            sub_payload = json.dumps(sub_data)
            
            try:
                await websocket.send(sub_payload)
                response = await websocket.recv()  
                print(response)
            
                while True:
                    try:                    
                        response = await websocket.recv()  
                        compressed_data = gzip.GzipFile(fileobj=io.BytesIO(response), mode='rb')
                        decompressed_data = compressed_data.read()
                        utf8_data = decompressed_data.decode('utf-8')                    

                        if utf8_data == "Ping": # this is very important , if you receive 'Ping' you need to send 'Pong' 
                            await websocket.send(pong_payload)
                        
                        else:
                            print(utf8_data)  #this is the message you need 
                                    
                            callback(utf8_data)                                                        

                    except Exception as ex:
                        print('exception from bingx_futures_socket_client.kline_subscribe: ', ex)   
                        break                               

            except websockets.ConnectionClosed:
                continue
            
            except Exception as ex_sub:
                print('exception from bingx_futures_socket_client.kline_subscribe: ', ex_sub) 
