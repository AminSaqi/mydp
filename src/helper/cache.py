
import pandas as pd


candles: 'dict[tuple[str, str, str], pd.DataFrame]' = {}


def get_data(exchange: str, symbol: str, timeframe: str, count: int):
    
    ex_sym_tf = (exchange, symbol, timeframe)

    if ex_sym_tf in candles:            
        return candles[ex_sym_tf].tail(count).copy()


