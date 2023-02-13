
from typing import TypeVar, Generic


T = TypeVar('T')


class ServiceResult(Generic[T]):

    def __init__(self, success: bool = None, result: T = None, message: str = None):

        self.success: bool = success
        self.result: T = result
        self.message: str = message
        
