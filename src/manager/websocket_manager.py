
from fastapi import WebSocket


class WebSocketManager:

    def __init__(self):
        self.__active_connections: dict[tuple[str, str, str], list[WebSocket]] = {}


    async def connect(self, exchange: str, symbol: str, timeframe: str, websocket: WebSocket):
        await websocket.accept()
        self.__active_connections[(exchange, symbol, timeframe)].append(websocket)

    def disconnect(self, exchange: str, symbol: str, timeframe: str, websocket: WebSocket):
        self.__active_connections[(exchange, symbol, timeframe)].remove(websocket)
    

    async def broadcast(self, exchange: str, symbol: str, timeframe: str, data: dict):
        connections = self.__active_connections[(exchange, symbol, timeframe)]
        for connection in connections:
            await connection.send_json(data)