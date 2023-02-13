
import os
import json

from fastapi import FastAPI

from src.service.data_service import DataService


#%% Service setup.


with open("config.json", "r") as f:
    config = json.load(f)    

data_service = DataService(config)


#%% FastAPI.


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/candles/{exchange}/{symbol}/{timeframe}/{count}")
async def candles(exchange: str, symbol: str, timeframe: str, count: int):
    return data_service.get_candles(exchange, symbol, timeframe, count)