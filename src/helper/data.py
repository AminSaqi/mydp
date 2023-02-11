
from src.base.enums import Exchange


class DataManager():

    def __init__(self, exchange: Exchange, quote_asset: str, timeframes: 'list[str]'):

        self.__exchange = exchange
        self.__quote_asset = quote_asset

        self.__api_client = None
        self.__listen_key = None
        self.__socket_client = None

        self.__setup_api_client()

        self.__symbols = self.__get_symbol_names()        

def setup_data_manager(exchange: Exchange, quote_asset: str):
    pass


