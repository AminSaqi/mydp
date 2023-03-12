
from fastapi import WebSocket

from src.manager.data_manager import DataManager
from src.manager.websocket_manager import WebSocketManager


class DataService():

    def __init__(self, config):
        self.__data_manager = DataManager(config, self.__push_data)
        self.__socket_manager = WebSocketManager()


    async def __push_data(self, exchange: str, symbol:str, timeframe: str, data: dict):
        await self.__socket_manager.broadcast(exchange, symbol, timeframe, data)


    async def connect_websocket(self, exchange: str, symbol: str, timeframe: str, websocket: WebSocket):
        await self.__socket_manager.connect(exchange, symbol, timeframe, websocket)

    async def disconnect_websocket(self, exchange: str, symbol: str, timeframe: str, websocket: WebSocket):
        await self.__socket_manager.disconnect(exchange, symbol, timeframe, websocket)


    def get_candles(self, exchange_name: str, symbol_name: str, timeframe: str, count: int):                        
        return self.__data_manager.get_candles(exchange_name, symbol_name, timeframe, count)