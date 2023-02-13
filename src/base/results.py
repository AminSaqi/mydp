
from typing import TypeVar, Generic

import pandas as pd


T = TypeVar('T')
Dict = TypeVar('Dict', dict)


class ServiceResult(Generic[T]):

    def __init__(self, success: bool = None, result: T = None, message: str = None):

        self.success: bool = success
        self.result: T = result
        self.message: str = message


class ApiResult(ServiceResult[Dict]):
    
    def __init__(self, service_result: ServiceResult[pd.DataFrame]=None, success: bool = None, result: Dict = None, message: str = None):    

        if service_result:    
            self.success = service_result.success
            self.result = service_result.result.to_dict(orient="records") if service_result.result else {}
            self.message = service_result.message
        else:
            self.success = success
            self.result = result
            self.message = message            


        
