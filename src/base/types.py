
from typing import Callable, Awaitable


DataEventFuncType = Callable[[str, str, str, dict], Awaitable[None]]