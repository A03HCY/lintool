from typing    import List, Optional, Callable
from functools import wraps


class Notify:
    def __init__(self) -> None:
        ...

    def notify(self, channel: str, kwargs: Optional[dict] = None) -> None:
        ...

    def when_executed(self, func:Callable, channel:str, contain_result:bool = False, kwargs:Optional[dict] = None) -> Callable:
        ...