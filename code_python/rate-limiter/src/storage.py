import abc
import time
import threading
from typing import Dict, Tuple

class RateLimitStorage(abc.ABC):
    """
    Abstract base class for rate limit storage backends.
    """

    @abc.abstractmethod
    def take_token(self, key: str, capacity: int, refill_rate: float, cost: int = 1) -> bool:
        """
        Atomically checks if enough tokens are available and consumes them.
        Returns True if allowed, False otherwise.

        Args:
            key: The unique identifier for the rate limit bucket (e.g., user ID or IP).
            capacity: The maximum number of tokens in the bucket.
            refill_rate: The number of tokens added per second.
            cost: The number of tokens required for this request.
        """
        pass

class InMemoryStorage(RateLimitStorage):
    """
    Thread-safe in-memory storage using Token Bucket algorithm.
    """

    def __init__(self):
        self._lock = threading.Lock()
        # Storage format: key -> (current_tokens, last_refill_time)
        self._buckets: Dict[str, Tuple[float, float]] = {}

    def take_token(self, key: str, capacity: int, refill_rate: float, cost: int = 1) -> bool:
        """
        Implements the token bucket algorithm with atomic updates.
        """
        with self._lock:
            current_time = time.monotonic()

            if key not in self._buckets:
                # Initial state: full bucket
                tokens = float(capacity)
                last_refill = current_time
            else:
                tokens, last_refill = self._buckets[key]

                # Refill tokens based on time elapsed
                elapsed = current_time - last_refill
                if elapsed < 0:
                    # Clock skew protection (unlikely with monotonic, but safe)
                    elapsed = 0

                added_tokens = elapsed * refill_rate
                tokens = min(float(capacity), tokens + added_tokens)
                last_refill = current_time

            if tokens >= cost:
                tokens -= cost
                self._buckets[key] = (tokens, last_refill)
                return True
            else:
                # Update state to reflect the refill, even if request is denied
                self._buckets[key] = (tokens, last_refill)
                return False
