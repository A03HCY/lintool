from typing import Callable
from functools import wraps
from time import sleep

def try_for(times: int, delay: int = 0) -> Callable:
    def decorator(func: Callable):
        if times == -1:
            max_attempts = float('inf')
        elif times < 1:
            raise ValueError("times must be at least 1 or -1 for infinite retries")
        else:
            max_attempts = times

        if delay < 0:
            raise ValueError("delay must be at least 0")

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            attempt = 0
            while True:
                try: return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    attempt += 1
                    if attempt >= max_attempts: break
                    if delay > 0: sleep(delay)
            if last_exception:
                raise last_exception
            else:
                raise RuntimeError("Function was not attempted")
        return wrapper
    return decorator


