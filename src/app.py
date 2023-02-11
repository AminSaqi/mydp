
import os
import json

from fastapi import FastAPI

from src.base.enums import Exchange
from src.helper.data import setup_data_manager
from src.helper.cache import get_data


#%% Data setup.

with open("config.json", "r") as f:
    config = json.load(f)    

setup_data_manager(config)


#%% FastAPI.

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/candles/{exchange}/{symbol}/{timeframe}/{count}")
async def candles(exchange: str, symbol: str, timeframe: str, count: int):
    return get_data(exchange, symbol, timeframe, count)