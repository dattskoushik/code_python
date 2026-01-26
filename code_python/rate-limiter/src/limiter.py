import functools
from typing import Callable, Any
from .storage import StorageBackend, InMemoryStorage

class RateLimiter:
    """
    Implements the Token Bucket algorithm for rate limiting.
    """
    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def allow_request(self, key: str, capacity: int, refill_rate: float) -> bool:
        """
        Checks if a request is allowed under the given capacity and refill rate.
        Delegates to the storage backend to ensure atomicity.

        Args:
            key (str): Unique identifier for the bucket.
            capacity (int): Maximum number of tokens the bucket can hold.
            refill_rate (float): Number of tokens added per second.

        Returns:
            bool: True if allowed, False otherwise.
        """
        return self.storage.take_token(key, capacity, refill_rate)

def limit_requests(
    key_func: Callable[..., str],
    capacity: int,
    refill_rate: float,
    storage: StorageBackend = None
):
    """
    Decorator to apply rate limiting to a function.

    Args:
        key_func: A function that takes the decorated function's args/kwargs
                  and returns a unique string key.
        capacity: Max tokens.
        refill_rate: Tokens per second.
        storage: Storage backend instance. If None, uses a new InMemoryStorage.
    """
    if storage is None:
        storage = InMemoryStorage()

    limiter = RateLimiter(storage)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if limiter.allow_request(key, capacity, refill_rate):
                return func(*args, **kwargs)
            else:
                raise RateLimitExceeded("Too many requests")
        return wrapper
    return decorator

class RateLimitExceeded(Exception):
    pass
