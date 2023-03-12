
import sys
sys.path.append('..')

import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.responses import Response

from src.service.data_service import DataService
from src.base.results import ApiResult


#%% Service setup.


with open("config.json", "r") as f:
    config = json.load(f)    

data_service = DataService(config)


#%% FastAPI.


app = FastAPI()


@app.get("/")
async def root() -> ApiResult:    
    return ApiResult(success=True)


@app.get("/candles/{exchange}/{symbol}/{timeframe}/{count}")
async def candles(exchange: str, symbol: str, timeframe: str, count: int, response: Response) -> ApiResult:
    
    data_result = data_service.get_candles(exchange, symbol, timeframe, count)
    api_result = ApiResult(data_result)

    if not api_result.success:
        response.status_code = status.HTTP_400_BAD_REQUEST

    return api_result


@app.websocket("/ws/{exchange}/{symbol}/{timeframe}")
async def websocket_candles(websocket: WebSocket, exchange: str, symbol: str, timeframe: str):
    await data_service.connect_websocket(exchange, symbol, timeframe, websocket)   