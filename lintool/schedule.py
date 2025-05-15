from typing    import List, Optional, Callable
from functools import wraps
from time      import sleep


def try_for(func: Callable, times: int, delay: int = 0) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(times):
            try:
                return func(*args, **kwargs)
            except Exception:
                pass
            finally:
                if delay: sleep(delay)
    return wrapper
