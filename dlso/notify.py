from typing import Dict, List, Optional, Callable, Any
from functools import wraps
from .data import Notification

class Notify:
    def __init__(self) -> None:
        self.channels: Dict[str, List[Callable]] = {}

    def notify(self, channel: str, kwargs: Optional[Dict[str, Any]] = None, noticer: Optional[str]='<notify>') -> None:
        """
        Trigger all callbacks registered to the specified channel.
        
        Args:
            channel: Channel name to notify.
            kwargs: Arguments to pass to the callbacks (default: None).
        """
        if channel not in self.channels:
            return
        for func in self.channels[channel]:
            notification = Notification(channel=channel, noticer=noticer, kwargs=kwargs)
            try:
                func(notification)
            except Exception as e:
                # Optional: Add logging here (e.g., logging.error(...))
                pass
    
    def when_notified(self, channel: str) -> Callable:
        """
        Decorator to register a function to a channel.
        The function will be called when the channel is notified.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if channel not in self.channels:
                    self.channels[channel] = []
                self.channels[channel].append(func)
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def when_executed(self, channel: str, data_kwargs: Optional[Dict[str, Any]] = None) -> Callable:
        """
        Decorator to notify a channel when the decorated function is executed.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                self.notify(channel, data_kwargs, noticer=func.__name__)
                return func(*args, **kwargs)
            return wrapper
        return decorator