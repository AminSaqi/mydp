
from src.manager.data_manager import DataManager


class DataService():

    def __init__(self, config):
        self.__data_manager = DataManager(config)


    def get_candles(self, exchange_name: str, symbol_name: str, timeframe: str, count: int):                        
        return self.__data_manager.get_candles(exchange_name, symbol_name, timeframe, count)