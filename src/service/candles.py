
from src.helper.cache import get_data


def get_candles(exchange: str, symbol: str, timeframe: str, count: int):
    
    df = get_data(exchange, symbol, timeframe, count)
    return df