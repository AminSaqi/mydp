
from fastapi import WebSocket


class WebSocketManager:

    def __init__(self):
        self.__active_connections: dict[tuple[str, str, str], list[WebSocket]] = {}


    async def connect(self, exchange: str, symbol: str, timeframe: str, websocket: WebSocket):
        await websocket.accept()

        key = (exchange, symbol, timeframe)
        if key not in self.__active_connections:
            self.__active_connections[key] = []

        self.__active_connections[key].append(websocket)

    def disconnect(self, exchange: str, symbol: str, timeframe: str, websocket: WebSocket):
        self.__active_connections[(exchange, symbol, timeframe)].remove(websocket)
    

    async def broadcast(self, exchange: str, symbol: str, timeframe: str, data: dict):  
        key = (exchange, symbol, timeframe)
        if key in self.__active_connections:
            connections = self.__active_connections[key]       
            for connection in connections:
                await connection.send_json(data)