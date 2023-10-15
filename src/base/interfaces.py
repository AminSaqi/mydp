
from abc import ABC, abstractmethod

import pandas as pd

from src.base.types import DataEventFuncType
from src.base.results import ServiceResult


class ExchangeProxy(ABC):

    @abstractmethod
    def __init__(self, symbols_config: 'list[dict]', push_data_event_func: DataEventFuncType):
        pass

    @abstractmethod
    def get_candles(self, symbol_name: str, timeframe: str, count: int) -> ServiceResult[pd.DataFrame] | ServiceResult[dict[pd.DataFrame]]:
        pass