
from abc import ABC, abstractmethod

import pandas as pd

from src.base.results import ServiceResult


class ExchangeProxy(ABC):

    @abstractmethod
    def get_candles(self, symbol_name: str, timeframe: str, count: int) -> ServiceResult[pd.DataFrame]:
        pass