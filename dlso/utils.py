from typing    import Callable
from functools import wraps
from time      import sleep
from re        import search
from .data     import EmailMatch
import random
import string

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


def email(email:str) -> EmailMatch:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matched_email = search(email_pattern, email)
    matched_email = matched_email.group() if matched_email else ''
    return EmailMatch(
        matched_email=matched_email,
        is_email=bool(matched_email == email)
    )


def safecode(num:int=6, pure_num:bool=False) -> str:
    if pure_num:
        return ''.join(random.choices(string.digits, k=num))
    else:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=num))

