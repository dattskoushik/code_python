from .storage import RateLimitStorage

class RateLimiter:
    """
    High-level Rate Limiter that delegates state management to a storage backend.
    """

    def __init__(self, storage: RateLimitStorage):
        self.storage = storage

    def allow_request(self, key: str, capacity: int, refill_rate: float, cost: int = 1) -> bool:
        """
        Checks if a request is allowed for the given key based on the token bucket algorithm.

        Args:
            key: Unique identifier for the user/IP/resource.
            capacity: Maximum number of tokens the bucket can hold (burst size).
            refill_rate: Number of tokens added to the bucket per second.
            cost: Number of tokens this request consumes. Defaults to 1.

        Returns:
            True if the request is allowed (tokens consumed).
            False if the request is denied (insufficient tokens).
        """
        return self.storage.take_token(key, capacity, refill_rate, cost)
