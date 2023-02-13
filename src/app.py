
import os
import json

from fastapi import FastAPI, status
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
async def root():    
    return Response(content=ApiResult(success=True))


@app.get("/candles/{exchange}/{symbol}/{timeframe}/{count}")
async def candles(exchange: str, symbol: str, timeframe: str, count: int):
    
    data_result = data_service.get_candles(exchange, symbol, timeframe, count)
    api_result = ApiResult(data_result)

    if api_result.success:
        return Response(content=api_result, status_code=status.HTTP_200_OK)
    else:
        return Response(content=api_result, status_code=status.HTTP_400_BAD_REQUEST)