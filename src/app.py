
import sys
sys.path.append('..')

import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.responses import Response, JSONResponse

from src.service.data_service import DataService
from src.base.results import ApiResult


app = FastAPI()


@app.on_event("startup")
def setup_data_Service():

    global data_service

    with open("config.json", "r") as f:
        config = json.load(f) 
        data_service = DataService(config) 


@app.get("/", response_class=JSONResponse)
async def root():    
    return vars(ApiResult(success=True))

@app.get("/candles/{exchange}/{symbol}/{timeframe}/{count}", response_class=JSONResponse)
async def candles(exchange: str, symbol: str, timeframe: str, count: int, response: Response):
    
    data_result = data_service.get_candles(exchange, symbol, timeframe, count)
    api_result = ApiResult(data_result)

    if not api_result.success:
        response.status_code = status.HTTP_400_BAD_REQUEST

    return vars(api_result)


@app.websocket("/ws/{exchange}/{symbol}/{timeframe}")
async def websocket_candles(websocket: WebSocket, exchange: str, symbol: str, timeframe: str):
  
    await data_service.connect_websocket(exchange, symbol, timeframe, websocket)  

    try:
        while True:            
            await websocket.receive_text()
            
    except WebSocketDisconnect:        
        data_service.disconnect_websocket(exchange, symbol, timeframe, websocket)
