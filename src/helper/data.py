
from src.base.enums import Exchange


class DataManager():

    def __init__(self, config: 'list[dict]'):

        self.__exchanges = {}

        for exchange_config in config:
            exchange_name = exchange_config['exchange']
            
            #TODO: check for valid exchange names.
            exchange = Exchange(exchange_name)

            symbols_config = exchange_config['symbols']
            
         
        self.__quote_asset = quote_asset

        self.__api_client = None
        self.__listen_key = None
        self.__socket_client = None

        self.__setup_api_client()

        self.__symbols = self.__get_symbol_names()        

def setup_data_manager(exchange: Exchange, quote_asset: str):
    pass


