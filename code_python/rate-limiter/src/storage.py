import abc
import time
import threading
from typing import Tuple, Optional

class StorageBackend(abc.ABC):
    """
    Abstract base class for rate limiter storage backends.
    """

    @abc.abstractmethod
    def take_token(self, key: str, capacity: int, refill_rate: float) -> bool:
        """
        Atomically attempts to consume a token from the bucket.

        Args:
            key (str): The unique identifier.
            capacity (int): Max tokens.
            refill_rate (float): Tokens per second.

        Returns:
            bool: True if token consumed (allowed), False otherwise.
        """
        pass


class InMemoryStorage(StorageBackend):
    """
    Thread-safe in-memory storage implementation.
    """

    def __init__(self):
        self._storage = {}
        self._lock = threading.Lock()

    def take_token(self, key: str, capacity: int, refill_rate: float) -> bool:
        with self._lock:
            current_time = time.monotonic()
            if key not in self._storage:
                tokens = float(capacity)
                last_updated = current_time
            else:
                tokens = self._storage[key]['tokens']
                last_updated = self._storage[key]['updated_at']

            # Calculate refill
            elapsed = current_time - last_updated
            refill_amount = elapsed * refill_rate
            tokens = min(float(capacity), tokens + refill_amount)

            if tokens >= 1.0:
                tokens -= 1.0
                self._storage[key] = {
                    'tokens': tokens,
                    'updated_at': current_time
                }
                return True
            else:
                # Update to checkpoint the refill progress even if we fail
                self._storage[key] = {
                    'tokens': tokens,
                    'updated_at': current_time
                }
                return False
