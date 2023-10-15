
from typing import TypeVar, Generic

import pandas as pd


T = TypeVar('T')
Dict = TypeVar('Dict', dict, None)


class ServiceResult(Generic[T]):

    def __init__(self, success: bool = None, result: T = None, message: str = None):

        self.success: bool = success
        self.result: T = result
        self.message: str = message


class ApiResult(ServiceResult[Dict]):
    
    def __init__(self, service_result: ServiceResult[pd.DataFrame] | ServiceResult[dict[pd.DataFrame]]=None, success: bool = None, result: Dict = None, message: str = None):    

        if service_result:    
            self.success = service_result.success

            if type(service_result.result) is pd.DataFrame:
                self.result = service_result.result.to_dict(orient="records") if (service_result.result is not None) else {}
            else:
                dict_result = {}
                for key, df in service_result.result.items():
                    dict_result[key] = df.to_dict(orient="records") if (service_result.result is not None) else {}
                self.result = dict_result

            self.message = service_result.message
        else:
            self.success = success
            self.result = result
            self.message = message            


        
